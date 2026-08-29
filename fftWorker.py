"""FFT frontend: turns a raw audio waveform chunk into a per-pixel frequency intensity
distribution mapped onto piano-key (musical note) bins instead of raw linear frequency bins.

Mapping frequencies to piano keys (rather than a linear FFT bin scale) is the core idea
behind acuvi: musical notes are spaced logarithmically in frequency, so this lets the
visualization line up with harmonics and octaves the way a listener actually perceives them,
instead of bunching all the musically-relevant low end into a handful of raw FFT bins.
"""

import math
import time as tm

import numba
import numpy as np
import scipy.fftpack

from sharedFunctions import *


class fftWorkerino:
    """Computes a normalized, piano-key-mapped frequency distribution from raw audio."""

    def __init__(self, RATE, RATE_FREQUENCY, NUM_PIXELS):
        self.RATE = RATE
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS
        # Rolling history of recent peak volumes, used to auto-normalize output levels.
        self.volume_history = np.zeros((2000,), dtype=np.float64)
        self.volume_history_pos = 0

        max_key = math.floor(freq_to_piano_key(self.RATE / 2))
        if max_key < NUM_PIXELS:
            print("num pixels is bigger than max key")
        print("fftWorker initialized")

    def fftWorker(self, audiosample):
        """Run an FFT on `audiosample` and return a normalized intensity value per pixel/key."""
        frequency_dist = np.zeros(self.NUM_PIXELS, dtype=float)
        fft_data = scipy.fftpack.rfft(audiosample)
        frequency_dist, self.volume_history, self.volume_history_pos = map_fft_to_freq_dist(
            self.RATE, audiosample, frequency_dist, fft_data,
            self.volume_history, self.volume_history_pos,
        )
        return frequency_dist


@numba.jit(nopython=True)
def freq_to_piano_key(freq):
    """Convert a frequency in Hz to its corresponding (fractional) piano key number."""
    key = 12 * np.log2((freq - 120) / 440)
    if key < 0:
        key = 0
    return round(key)


@numba.jit(nopython=True)
def piano_key_to_freq(key):
    """Convert a piano key number back to a frequency in Hz (inverse of freq_to_piano_key)."""
    return 440 * np.power(2, (key - 49) / 12) + 120


@numba.jit(nopython=True)
def map_fft_to_freq_dist(RATE, audiosample, frequency_dist, fft_data, volume_history, volume_history_pos):
    """Bucket raw FFT output into one intensity value per piano key, then normalize."""
    step = RATE / len(audiosample)

    for j in range(frequency_dist.size):
        freq = piano_key_to_freq(j)
        next_freq = piano_key_to_freq(j + 1)
        chunk = fft_data[int(freq / step):int(next_freq / step)]
        value = 0
        if np.any(chunk):
            value = np.sum(np.abs(chunk))
        frequency_dist[j] = value

    frequency_dist, volume_history, volume_history_pos = normalize(
        frequency_dist, volume_history, volume_history_pos
    )
    return frequency_dist, volume_history, volume_history_pos


@numba.jit(nopython=True)
def normalize(frequency_dist, volume_history, volume_history_pos):
    """Scale intensities to roughly [0, 1] using a rolling average of recent peak volume,
    so the visualization stays consistent across quiet and loud passages."""
    if np.any(frequency_dist):
        max_value = np.max(frequency_dist)
        volume_history[volume_history_pos] = max_value
        mean_volume = np.mean(volume_history)

        if mean_volume < 10000:
            frequency_dist = frequency_dist / 10000
        else:
            frequency_dist = frequency_dist / mean_volume

        volume_history_pos += 1
        if volume_history_pos >= 2000:
            volume_history_pos = 0

    return frequency_dist, volume_history, volume_history_pos
