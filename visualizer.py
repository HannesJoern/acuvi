"""Turns a per-pixel frequency distribution into actual RGB colors for display.

Handles: temporal smoothing (so colors rise/fall smoothly instead of flickering frame to
frame), a configurable exponent/gain curve, and a fixed low/mid/high color mapping so bass
frequencies render blue, mids render red/green, and highs render white.
"""

import csv
import os
import time as tm

import numba
import numpy as np

from sharedFunctions import *

# Live-tunable parameters (brightness, smoothing, etc.) are read from this CSV file,
# which the Dash UI in server.py writes to. This lets you tweak the look of the
# visualization while it's running, without restarting the process.
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.csv")


class Visualizer:
    """Converts a frequency distribution into a colored, temporally-smoothed pixel array."""

    def __init__(self, RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS):
        self.RATE = RATE
        self.RATE_INTENSITY = RATE_INTENSITY
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS
        self.r_down_intens = self.RATE / self.RATE_INTENSITY
        self.r_down_freq = self.RATE / self.RATE_FREQUENCY
        self.max_rgb = 255

        self.prev_values = np.zeros(self.NUM_PIXELS)

        # Tunable parameters, overwritten by readConfig() from data.csv.
        self.norm_factor = 0.01   # overall brightness scaling
        self.rise_fac = 0.9       # temporal smoothing when intensity increases
        self.fall_fac = 0.9       # temporal smoothing when intensity decreases
        self.exponent = 1         # gain curve exponent, sharpens/softens response
        self.lower_part = 1       # scaling applied to low (bass) frequencies
        self.upper_part = 1       # scaling applied to high (treble) frequencies

        # How often (in calls to visualize()) to re-read the config file from disk.
        self.readconfigcounter = 0
        self.READCONFIG_INTERVAL = 10

    def readConfig(self):
        """Reload the tunable parameters from data.csv, written live by the Dash UI."""
        try:
            with open(CONFIG_PATH, 'r', newline='') as f:
                rd = csv.reader(f, delimiter=',')
                for row in rd:
                    self.norm_factor = float(row[0])
                    self.rise_fac = float(row[1])
                    self.fall_fac = float(row[2])
                    self.exponent = float(row[3])
                    self.upper_part = float(row[4])
                    self.lower_part = float(row[5])
        except (OSError, ValueError, IndexError):
            print("couldn't read config file, keeping previous values")

    def visualize(self, waveform, frequency_dist):
        """Produce one frame of RGB values (shape: NUM_PIXELS x 3) for the given frequency data."""
        if self.readconfigcounter >= self.READCONFIG_INTERVAL:
            self.readConfig()
            self.readconfigcounter = 0
        else:
            self.readconfigcounter += 1

        self.prev_values, keyboard_visualization = self.createKeyboardVisualization(
            frequency_dist, self.prev_values, self.norm_factor,
            self.rise_fac, self.fall_fac, self.exponent,
        )
        return keyboard_visualization

    def createKeyboardVisualization(self, frequency_dist, prev_values, norm_factor, rise_fac, fall_fac, exponent):
        """Apply the gain curve, then convert to smoothed, colored pixel values."""
        keyboard_visualization = np.zeros((self.NUM_PIXELS, 3), dtype=float)
        frequency_dist = applyExponentAndUpperLower(
            frequency_dist, exponent, self.upper_part, self.lower_part
        )
        keyboard_visualization, prev_values = applyColorsAndFallRise(
            norm_factor, prev_values, frequency_dist, keyboard_visualization,
            rise_fac, fall_fac, self.NUM_PIXELS,
        )
        return prev_values, keyboard_visualization


@numba.jit(nopython=True)
def applyExponentAndUpperLower(frequency_dist, exponent, upper_part, lower_part):
    """Scale the low/high ends of the spectrum independently, then apply the gain exponent."""
    for j in range(len(frequency_dist) - 1):
        if j < 36:
            frequency_dist[j] = frequency_dist[j] * lower_part
        if j > 100:
            frequency_dist[j] = frequency_dist[j] * upper_part
        frequency_dist[j] = frequency_dist[j] ** exponent
    return frequency_dist


@numba.jit(nopython=True)
def applyColorsAndFallRise(norm_factor, prev_values, frequency_dist, keyboard_visualization, rise_fac, fall_fac, no_pixels):
    """Map each pixel's intensity to an RGB color based on its position in the spectrum
    (bass = blue, low-mid = blue/red blend, mid = red/green blend, high-mid = green/blue
    blend, treble = white), and smooth each pixel's brightness over time so it rises/falls
    gradually instead of flickering with every frame.
    """
    intensity = 400

    for j in range(no_pixels):
        value = np.abs(frequency_dist[j] * norm_factor) * intensity

        # Color mapping by frequency band.
        if j < 40:
            redfac, greenfac, bluefac = 0.0, 0.0, 1.0
        elif j < 60:
            redfac = np.power(float(j - 40) / 20, 1)
            greenfac = 0.0
            bluefac = np.power(float(60 - j) / 20, 1)
        elif j <= 80:
            redfac = np.power(float(80 - j) / 20, 1)
            greenfac = np.power(float(j - 60) / 20, 1)
            bluefac = 0.0
        elif j <= 100:
            redfac = 0.0
            greenfac = np.power(float(100 - j) / 20, 1)
            bluefac = np.power(float(j - 80) / 20, 1)
        else:
            redfac, greenfac, bluefac = 1.0, 1.0, 1.0

        # Temporal smoothing: ease towards the new value instead of jumping straight to it.
        if value < prev_values[j]:
            value = value + (prev_values[j] - value) * fall_fac
        else:
            value = value - (value - prev_values[j]) * rise_fac
        prev_values[j] = value

        value = min(max(value, 0), 255)

        keyboard_visualization[j] = np.array([int(redfac * value), int(greenfac * value), int(bluefac * value)])

    return keyboard_visualization, prev_values
