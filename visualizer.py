import numpy as np
from sharedFunctions import *
import numba
import time as tm
#import matplotlib.pyplot as plt
import scipy.ndimage
import scipy.signal
import csv

class Visualizer():
    def __init__(self, RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS):
        #current params
        self.RATE = RATE
        self.RATE_INTENSITY = RATE_INTENSITY
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS
        self.empty_color_val = np.array([0 for i in range(3)])
        self.r_down_intens = self.RATE/self.RATE_INTENSITY
        self.r_down_freq = self.RATE/self.RATE_FREQUENCY
        self.max_rgb = 255

        self.prev_values = np.array([0 for i in range(self.NUM_PIXELS)])
        self.prev_intensities = []
        self.prev_frequency_dist = np.array([0 for i in range(self.NUM_PIXELS)])
        self.frequency_dist = np.array([0 for i in range(self.NUM_PIXELS)])
        self.norm_factor = 0.01 #normalization factor
        self.rise_fac = 0.9
        self.fall_fac = 0.9
        self.exponent = 1
        self.lower_part = 1
        self.upper_part = 1
        self.kernel = [ 
            0.00007829675330892041, 
            0.0015726323295519597, 
            0.016217391109881296, 
            0.08586281587584525, 
            0.23339933213563108, 
            0.32573500793527993, 
            0.23339933213563108, 
            0.08586281587584525, 
            0.016217391109881296, 
            0.0015726323295519597
        ]
        self.smol_kernel = [
            0.23874320576678076, 
            0.44603102903819275, 
            0.23874320576678076
        ]
        self.readconfigcounter = 0
        
        #print("visualizer initialized!")

    def readConfig(self):
        try:
            with open('/home/hannes/Desktop/acuvi-repo/acuvi/data.csv', 'r', newline='') as f:
                rd = csv.reader(f, delimiter = ',')
                for row in rd:
                    self.norm_factor = float(row[0])
                    self.rise_fac = float(row[1])
                    self.fall_fac = float(row[2])
                    self.exponent = float(row[3])
                    self.upper_part = float(row[4])
                    self.lower_part = float(row[5])
                f.close()
                return

        except:
            print("couldnt access file")

    def visualize(self, waveform, frequency_dist):
        time_begin = tm.perf_counter()
        if self.readconfigcounter == 10:
            self.readConfig()
            self.readconfigcounter = 0
        else:
            self.readconfigcounter += 1
        visualization = np.array([[0 for i in range(3)] for i in range(self.NUM_PIXELS)])
        keyboard_visualization = np.array([[0 for j in range(3)] for i in range(self.NUM_PIXELS)], dtype = float)
        self.previous_values, keyboard_visualization = self.createKeyboardVisualization(waveform, frequency_dist, self.prev_values, self.norm_factor, keyboard_visualization, self.rise_fac, self.fall_fac, self.exponent, self.upper_part, self.lower_part)
        visualization = keyboard_visualization
        time_end = tm.perf_counter()
        #print("visualizer time: " + str(time_end - time_begin))
        return visualization



    def createKeyboardVisualization(self, waveform, frequency_dist, prev_values, norm_factor, keyboard_visualization, rise_fac, fall_fac, exponent, upper_part, lower_part):
        intensity = 0
        if np.any(waveform):
            intensity = np.log(np.max(np.abs(waveform)))

        redfac = 1
        greenfac = 1
        bluefac = 1
        upper_part = self.upper_part
        lower_part = self.lower_part
        frequency_dist = applyExponentAndUpperLower(frequency_dist, exponent, upper_part, lower_part)
        #print("intensity is: " +str(intensity))

        #frequency_dist[0:140] = scipy.ndimage.convolve(frequency_dist[0:140], self.kernel)

        keyboard_visualization, prev_values = applyColorsAndFallRise(norm_factor, prev_values, frequency_dist, keyboard_visualization, rise_fac, fall_fac, self.NUM_PIXELS)
        return prev_values, keyboard_visualization

@numba.jit(nopython=True)
def applyExponentAndUpperLower(frequency_dist, exponent, upper_part, lower_part):
    for j in range(len(frequency_dist) - 1):
        if j < 36:
            frequency_dist[j] = frequency_dist[j] * lower_part
        if j > 100:
            frequency_dist[j] = frequency_dist[j] * upper_part
        frequency_dist[j] = frequency_dist[j]**exponent
    return frequency_dist

@numba.jit(nopython=True)
def applyColorsAndFallRise(norm_factor, prev_values, frequency_dist, keyboard_visualization, rise_fac, fall_fac, no_pixels):
    redfac = 1
    greenfac = 1
    bluefac = 1

    fall_add_factor = fall_fac
    rise_sub_factor = rise_fac
    for j in range(no_pixels):
        redfac = 1
        greenfac = 1
        bluefac = 1
        intensity = 255
        fall_add_factor = fall_fac
        rise_sub_factor = rise_fac
        value = np.abs(frequency_dist[j] * norm_factor) * intensity

        if j < 35:
            redfac = 0
            greenfac = 0
            bluefac = 1
        if j >= 35 and j < 50:
            redfac = np.power(float(j - 35)/15, 1)
            greenfac = 0
            bluefac = np.power(float(50 - j)/15, 1)
        if j >= 50 and j <= 65:
            redfac = np.power(float(65 - j)/15, 1)
            greenfac = np.power(float(j - 50)/15, 1)
            bluefac = 0
        if j >= 65 and j <= 80:
            redfac = 0
            greenfac = np.power(float(80 - j)/15, 1)
            bluefac = np.power(float(j - 65)/15, 1)

        # highs
        if j>85:
            bluefac = 1
            redfac = 1
            greenfac = 1
    
        if value < prev_values[j]:
            value = value + (prev_values[j] - value)*fall_add_factor
        else:
            value = value - (value - prev_values[j])*rise_sub_factor
        
            
        prev_values[j] = value


        rgb_max = 255
        if value > rgb_max:
            value = 255
        if value < 0:
            value = 0

        keyboard_visualization[j] = np.array([int(redfac*value), int(greenfac*value), int(bluefac*value)])
    return keyboard_visualization, prev_values
