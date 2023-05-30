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
        intensity = 400
        fall_add_factor = fall_fac
        rise_sub_factor = rise_fac
        if j < 20:
            rise_sub_factor = rise_fac * 0.9
            fall_add_factor = fall_fac * 0.9
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power((20 - j)/20, 2)
            bluefac = 1
            value = np.abs(frequency_dist[j] * norm_factor) * intensity


        if j >= 20 and j < 40:
            rise_sub_factor = rise_fac * 0.9
            fall_add_factor = fall_fac * 0.9
            redfac = 1 * np.power(j / 40, 2) * 1.2
            greenfac = 1 * np.power(j / 80, 2)
            bluefac = 1
            value = np.abs(frequency_dist[j] * norm_factor) * intensity

        if j>=40 and j<60:
            redfac = 1 * 1.5
            greenfac = 1 * np.power(j/80, 2)
            #bluefac = 1 * np.power((80 - j)/60, 2)
            bluefac = 0
            value = np.abs(frequency_dist[j] * norm_factor) * intensity


        if j>=60 and j<80:
            redfac = 1 * np.power((80 - j)/20, 2) * 1.2
            greenfac = 1 * np.power(j/80, 2)
            #bluefac = 1 * np.power((80 - j)/40, 2)
            bluefac = 0
            value = np.abs(frequency_dist[j] * norm_factor) * intensity


        if j>=80 and j<90:
            redfac = 0.9 * np.power((j - 80)/10, 2)
            greenfac = 0.8
            bluefac = 0.8 * np.power((j - 80)/10, 3)
            value = np.abs(frequency_dist[j] * norm_factor) * intensity

        if j>=100:
            redfac = 1
            greenfac = 1
            bluefac = 1
            value = np.abs(frequency_dist[j] * norm_factor) * intensity
            rise_sub_factor = rise_fac * 0.9
            fall_add_factor = fall_fac * 0.9

        if j < 36:
            bluefac = 1
            greenfac = 0.5*np.power((36-j)/24, 2)
            redfac = 0.5*np.power(j/36, 2)

        if j >= 36 and j < 48:
            bluefac = np.power((48 - j)/24, 2)
            redfac = np.power((j - 36)/24, 2)
            greenfac = 0
            value = value * np.power((j - 36)/12, 2)
        

        """if j >= 48 and j < 60:
            bluefac = np.power((48 - j)/24, 2)
            redfac = np.power((j - 36)/24, 2)
            greenfac = 0
        if j >= 60 and j < 72:
            bluefac = 0
            redfac = np.power((72 - j)/12, 2)
            greenfac = np.power((j - 60)/12, 2)

        if j >= 72 and j < 84:
            bluefac = np.power((j - 72)/12, 2)
            redfac = 0
            greenfac = 1
            value = value * np.power((84-j)/12, 2)"""
        if j >= 48 and j < 60:
            if j >= 48 and j < 54:
                bluefac = 0
                redfac = np.power((j - 48)/6, 2)
                greenfac = np.power((54 - j)/6, 2)
            if j >= 54 and j < 60:
                bluefac = 0
                redfac = np.power((60 - j)/6, 2)
                greenfac = np.power((j - 54)/6, 2)
        if j >= 60 and j < 72:
            if j >= 60 and j < 66:
                bluefac = 0
                redfac = np.power((j - 60)/6, 2)
                greenfac = np.power((66 - j)/6, 2)
            if j >= 66 and j < 72:
                bluefac = 0
                redfac = np.power((72 - j)/6, 2)
                greenfac = np.power((j - 66)/6, 2)
        if j >= 72 and j < 84:
            if j >= 72 and j < 78:
                bluefac = 0
                redfac = np.power((j - 72)/6, 2)
                greenfac = np.power((78 - j)/6, 2)
            if j >= 78 and j < 84:
                bluefac = 0
                redfac = np.power((84 - j)/6, 2)
                greenfac = np.power((j - 87)/6, 2)
        if j > 84:
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
