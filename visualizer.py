import numpy as np
from sharedFunctions import *
import numba
import time as tm
import matplotlib.pyplot as plt
import scipy.ndimage
import scipy.signal

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

        self.prev_values = np.array([0 for i in range(142)])
        self.prev_intensities = []
        self.prev_frequency_dist = np.array([0 for i in range(142)])
        self.frequency_dist = np.array([0 for i in range(142)])
        self.intensity_fac = 100
        self.norm_factor = 1 #normalization factor
        print("visualizer initialized!")

    def visualize(self, waveform, frequency_dist):
        time_begin = tm.perf_counter()
        visualization = np.array([[0 for i in range(3)] for i in range(self.NUM_PIXELS)])
        keyboard_visualization = np.array([[0 for j in range(3)] for i in range(142)], dtype = float)
        self.previous_values, keyboard_visualization, self.intensity_fac, self.prev_intensities = createKeyboardVisualization(waveform, frequency_dist, self.prev_values, self.norm_factor, keyboard_visualization, self.intensity_fac, self.prev_intensities)
        visualization[0:141] = keyboard_visualization[1:]
        time_end = tm.perf_counter()
        print("visualizer time: " + str(time_end - time_begin))
        return visualization

def getHarmonics(spectrum):
    for i in range(len(spectrum)):
        spectrum[i%12] += spectrum[i]
    spectrum_harmonics = spectrum[:12]
    return spectrum_harmonics

def getSpectrumIntensity(spectrum):
    return np.sum(spectrum)

def getHarmonicPeaks(spectrum_harmonics):
    return scipy.signal.find_peaks(spectrum_harmonics, prominence = 0.8)[0]

def mapHarmonics(harmonicPeaks, intensity):
    #intensity in 0...255
    rep = np.zeros(24)
    # peak in 0...11
    for peak in harmonicPeaks:
        peak = 2 * peak
        # peak in 0...22
        offset = 5
        for i in range(offset):
            if i == 0 and peak + offset < len(rep) - 1:
                rep[peak + offset] = intensity/i
            else:
                if peak + offset - i >= 0 and peak + offset - i < len(rep) - 1:
                    rep[peak + offset - i] = intensity/i**2
                if peak + offset + i < len(rep) - 1 and peak + offset + i >= 0:
                    rep[peak + offset + i] = intensity/i**2
    return rep


#@numba.jit(nopython=True)
def createKeyboardVisualization(waveform, frequency_dist, prev_values, norm_factor, keyboard_visualization, intensity_fac, prev_intensities):


    intensity = 0
    if np.any(waveform):
        intensity = np.log(np.max(np.abs(waveform))) * intensity_fac
    print("intensity: " + str(intensity))
    print("intensity faq is: " + str(intensity_fac))

    if len(prev_intensities) < 100:
        prev_intensities.append(intensity)
    else:
        prev_intensities.pop(0)
        prev_intensities.append(intensity)
    
    ideal_value = 10000
    offset = 5000
    mean_intensity = np.mean(prev_intensities)
    if mean_intensity < ideal_value - offset or mean_intensity > ideal_value + offset:
        intensity_fac = ideal_value/mean_intensity


    redfac = 1
    greenfac = 1
    bluefac = 1
    
    """spectras = [frequency_dist[30:60], frequency_dist[60:90]]

    reps = []
    for spectrum in spectras:
        harmonic = getHarmonics(spectrum)
        harmonic_peaks = getHarmonicPeaks(harmonic)
        intensity = getSpectrumIntensity(spectrum)
        reps.append(mapHarmonics(harmonic_peaks, intensity))
    print(reps)
    
    
    values = np.zeros(len(keyboard_visualization) + 1)

    for i in range(len(reps)):
        values[i*len(reps[0]):i*len(reps[0]) + len(reps[i])] = reps[i]"""
    kernel = [ 
        0.0000014867217352114659, 
        0.00013383042564586007, 
        0.004431855031086564, 
        0.05399104715092312, 
        0.24197108591239316, 
        0.39894287623816743, 
        0.24197108591239316, 
        0.05399104715092312, 
        0.004431855031086564, 
        0.00013383042564586007
    ]
    smol_kernel = [
        0.23874320576678076, 
        0.44603102903819275, 
        0.23874320576678076
    ]
    frequency_dist[0:110] = scipy.ndimage.convolve(frequency_dist[0:110], kernel)
    frequency_dist[100:] = scipy.ndimage.convolve(frequency_dist[100:], smol_kernel)

    for j in range(142):
        
        norm_factor = 1
        redfac = 1
        greenfac = 1
        bluefac = 1

        fall_add_factor = 0.8
        if j < 20:
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power((20 - j)/20, 2)
            bluefac = 1
            norm_factor = 4
            value = np.abs(frequency_dist[j] * intensity * norm_factor)
            temp_factor = 0.3
            fall_add_factor = 0.3

        if j >= 20 and j < 40:
            redfac = 1 * np.power(j / 40, 2)
            greenfac = 1 * np.power(j / 80, 2)
            bluefac = 1
            norm_factor = 4
            value = np.abs(frequency_dist[j] * intensity * norm_factor)
            temp_factor = 0.9

        if j>=40 and j<60:
            redfac = 1
            greenfac = 1 * np.power(j/80, 2)
            bluefac = 1 * np.power((80 - j)/60, 2)
            norm_factor = 3

            value = np.abs(frequency_dist[j] * intensity * norm_factor)
            temp_factor = 0.9


        if j>=60 and j<80:
            redfac = 1 * np.power((80 - j)/20, 2)
            greenfac = 1 * np.power(j/80, 2)
            bluefac = 1 * np.power((80 - j)/40, 2)
            norm_factor = 3

            value = np.abs(frequency_dist[j] * intensity * norm_factor)
            temp_factor = 0.9


        if j>=80 and j<90:
            redfac = 0.9 * np.power((j - 80)/10, 2)
            greenfac = 0.8
            bluefac = 0.8 * np.power((j - 80)/10, 3)
            norm_factor = 3

            value = np.abs(frequency_dist[j] * intensity * norm_factor)
            temp_factor = 0.85

        if j>=90 and j<142:
            redfac = 1
            greenfac = 1
            bluefac = 1
            norm_factor = 3
            value = np.abs(frequency_dist[j]**2 * intensity * norm_factor)
            temp_factor = 0.4

        rise_sub_factor = temp_factor
        
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
        

    """for l in range(keyboard_visualization.size):
        donothing = 0
        if l == 0:
            donothing = 1
        if l >= 0 and l < 139:
            keyboard_visualization[l] += keyboard_visualization[l-1]/5 + keyboard_visualization[l+1]/5
        if l == keyboard_visualization.size - 1:
            donothing = 1"""
    
    return prev_values, keyboard_visualization, intensity_fac, prev_intensities
