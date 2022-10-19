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

        self.prev_values = np.array([0 for i in range(142)])
        self.prev_intensity = 0
        self.prev_frequency_dist = np.array([0 for i in range(142)])
        self.frequency_dist = np.array([0 for i in range(142)])

        self.norm_factor = 0.5 #normalization factor
        self.frequency_dist_queue = frequency_dist_queue
        print("visualizer initialized!")

    def visualize(self, waveform):
        visualization = np.array([[0 for i in range(3)] for i in range(self.NUM_PIXELS)])
        while not self.frequency_dist_queue.empty():
            self.frequency_dist = self.frequency_dist_queue.get()
        keyboard_visualization = np.array([[0 for j in range(3)] for i in range(142)], dtype = float)
        self.previous_values, keyboard_visualization = createKeyboardVisualization(waveform, self.frequency_dist, self.prev_values, self.norm_factor, keyboard_visualization)
        visualization[0:141] = keyboard_visualization[1:]



        return visualization
        
@numba.jit(nopython=True)
def createKeyboardVisualization(waveform, frequency_dist, prev_values, norm_factor, keyboard_visualization):
    intensity = 0
    if np.any(waveform):
        intensity = np.max(np.abs(waveform))
    redfac = 1
    greenfac = 1
    bluefac = 1
    

    for j in range(142):

        value = np.abs(np.power(frequency_dist[j], 3) * intensity * norm_factor)
        temp_factor = 0.9
        value = value + temp_factor * prev_values[j]

        if j < 20:
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power((20 - j)/20, 2)
            bluefac = 1
            value = np.abs(np.power(frequency_dist[j], 2) * intensity * norm_factor)
            temp_factor = 0.65
            value = value + temp_factor * prev_values[j]

        if j >= 20 and j < 40:
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power(j / 60, 2)
            bluefac = 1
            value = np.abs(np.power(frequency_dist[j], 2) * intensity * norm_factor)
            temp_factor = 0.75
            value = value + temp_factor * prev_values[j]

        if j>=40 and j<60:
            redfac = 1
            greenfac = 1 * np.power(j/60, 2)
            bluefac = 1 * np.power((80 - j)/60, 2)

        if j>=60 and j<80:
            redfac = 1 * np.power((80 - j)/20, 2)
            greenfac = 1
            bluefac = 1 * np.power((80 - j)/40, 2)

        if j>=80 and j<100:
            redfac = 1 * np.power((j - 80)/20, 2)
            greenfac = 1
            bluefac = 1 * np.power((j - 80)/20, 2)

        if j>=100 and j<142:
            redfac = 1
            greenfac = 1
            bluefac = 1

            value = np.abs(np.power(frequency_dist[j], 5) * intensity * norm_factor)
            temp_factor = 0.65
            value = value + temp_factor * prev_values[j]
        
        rgb_max = 255
        if value > rgb_max:
            value = 255
        if value < 0:
            value = 0

        keyboard_visualization[j] = np.array([int(redfac*value), int(greenfac*value), int(bluefac*value)])
        prev_values[j] = value

    keyboard_visualization = spatial_blurring(keyboard_visualization)
    return prev_values, keyboard_visualization


@numba.jit(nopython=True)
def spatial_blurring(keyboard_visualization):
    alternative_hack_to_pass_keyword = 0
    for l in range(142):
        if l == 0:
            alternative_hack_to_pass_keyword = 1
        if l >= 0 and l < 139:
            keyboard_visualization[l] = keyboard_visualization[l] + keyboard_visualization[l-1]/5 + keyboard_visualization[l+1]/5
        if l == 141:
            alternative_hack_to_pass_keyword = 1
    return keyboard_visualization
