import numpy as np
from sharedFunctions import *
import numba

class Visualizer():
    def __init__(self, RATE, RATE_INTENSITY, RATE_FREQUENCY, frequency_dist_queue, NUM_PIXELS):
        #current params
        self.RATE = RATE
        self.RATE_INTENSITY = RATE_INTENSITY
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS
        self.empty_color_val = np.array([0 for i in range(3)])
        self.r_down_intens = self.RATE/self.RATE_INTENSITY
        self.r_down_freq = self.RATE/self.RATE_FREQUENCY
        self.max_rgb = 255

        self.prev_values = np.array([0 for i in range(120)])
        self.prev_intensity = 0
        self.prev_frequency_dist = np.array([0 for i in range(120)])
        self.frequency_dist = np.array([0 for i in range(120)])

        self.norm_factor = 1 #normalization factor
        self.frequency_dist_queue = frequency_dist_queue
        print("visualizer initialized!")

    def visualize(self, waveform):
        visualization = np.array([[0 for i in range(3)] for i in range(self.NUM_PIXELS)])
        while not self.frequency_dist_queue.empty():
            self.frequency_dist = self.frequency_dist_queue.get()

        self.previous_values, keyboard_visualization, strobo = createKeyboardVisualization(waveform, self.frequency_dist, self.prev_values, self.norm_factor)
        visualization[:120] = keyboard_visualization
        strobos = np.array([[strobo for i in range(3)] for j in range(12)])
        trans = np.array([[j/10*strobo for i in range(3)] for j in range(10)])
        visualization[120:120+10] = trans
        visualization[130:130+12] = strobos
        return visualization
@numba.jit
def createKeyboardVisualization(waveform, frequency_dist, prev_values, norm_factor):
    intensity = 0
    if np.any(waveform):
        intensity = np.max(np.abs(waveform))
    redfac = 1
    greenfac = 1
    bluefac = 1
    keyboard_visualization = np.array([[0 for j in range(3)] for i in range(120)])

    for j in range(120):

        value = np.abs(np.power(frequency_dist[j], 3) * intensity * norm_factor)
        temp_factor = 0.95
        value = value + temp_factor * prev_values[j]

        if j<40:
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power(j / 80, 2)
            bluefac = 1
        if j>=40 and j<80:
            redfac = 1
            greenfac = 1 * np.power(j/80, 2)
            bluefac = 1 * np.power((120 - j)/80, 2)
        if j>=80 and j<120:
            redfac = 1 * np.power((120 - j)/40, 2)
            greenfac = 1
            bluefac = 1 * np.power((120 - j)/80, 2)
        
        rgb_max = 255
        if value > rgb_max:
            value = 255
        if value < 0:
            value = 0

        keyboard_visualization[j] = np.array([int(redfac*value), int(greenfac*value), int(bluefac*value)])
        prev_values[j] = value

    return prev_values, keyboard_visualization, intensity * 0.008