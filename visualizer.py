import numpy as np
from sharedFunctions import *
import math
import crepe
import numba

class Visualizer():
    def __init__(self, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS):
        self.RATE = RATE
        self.CHUNKSIZE = CHUNKSIZE
        self.CHUNKTIME = CHUNKTIME
        self.FPS = FPS
        self.NUM_PIXELS = NUM_PIXELS
        self.max_rgb = 255

        self.empty_color_val = np.array([0 for i in range(3)])
        self.len_vis = FPS*CHUNKTIME #size of chunk of vis_samples
        self.prev_intensities = np.array([[[0 for i in range(self.len_vis)] for j in range(2)] for k in range(4)])
        self.r_down = RATE/FPS #downsampling rate
        self.norm_factor = 15 #normalization factor
    def visualize(self, waveform):
        #visualization pipeline with crepe:
        audio_right = waveform[:,0]

        hopsize = self.CHUNKTIME*1000/(self.len_vis/2 - 1)
        time, frequency, confidence, activation = crepe.predict(audio_right, self.RATE, viterbi = True, model_capacity='tiny', step_size=hopsize)


        if frequency.size != self.len_vis:
            print("hop size in crepe is defined wrong with crepe array - len_vis = " + str(frequency.size - self.len_vis))

        #initialize keyboard visualization:
        
        visualization = np.array([[[0 for i in range(3)] for i in range(self.NUM_PIXELS)] for j in range(self.len_vis)])
        keyboard_visualization = np.array([[[0 for i in range(3)] for k in range(120)] for j in range(self.len_vis)])
        prev_temp = np.array([0 for i in range(120)])

        for i in range (self.len_vis):
            start = int(i*self.r_down)
            stop = int((i+1)*self.r_down-1)
            sample_left = waveform[start:stop,0]

            intensity = 0
            if np.any(sample_left):
                intensity = np.max(np.abs(sample_left))

            temp = 0
        
            for j in range(120):

                temp, prev_temp = numbaFunction(i, j, temp, activation, intensity, self.norm_factor, prev_temp)

                keyboard_visualization[i][j] = np.array([int(temp), int(temp), int(temp)])

                prev_temp[j] = temp
            
                temp = 0

            visualization[i][10:130] = keyboard_visualization[i]
        return visualization

@numba.jit()
def numbaFunction(i, j, temp, activation, intensity, norm_factor, prev_temp):
    for k in range(3):
        temp += np.power(activation[math.floor(i/2)][j*k+k], 3)          

    temp = temp * intensity * norm_factor
    temp_factor = 0.8

    temp += prev_temp[j] * temp_factor
    rgbmax = 255
    if temp > rgbmax:
        temp = rgbmax
    
    return temp, prev_temp
