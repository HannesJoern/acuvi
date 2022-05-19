import numpy as np
from sharedFunctions import *

import matplotlib.pyplot as plt

class Visualizer():
    def __init__(self, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS):
        self.RATE = RATE
        self.CHUNKSIZE = CHUNKSIZE
        self.CHUNKTIME = CHUNKTIME
        self.FPS = FPS
        self.NUM_PIXELS = NUM_PIXELS
        self.max_rgb = 255


        self.len_vis = FPS*CHUNKTIME #size of chunk of vis_samples
        self.prev_vis_data = np.array([[[0 for i in range(self.len_vis)] for j in range(2)] for k in range(4)])
        self.r_down = RATE/FPS #downsampling rate
        init_norm_factor = 1 #normalization factor
        self.norm_factors = np.array([init_norm_factor for i in range(4)])


    def visualize(self, spleeter_data):

        #convert into array
        vocals = np.array([spleeter_data['vocals'][:,0], spleeter_data['vocals'][:,1]])
        other = np.array([spleeter_data['other'][:,0], spleeter_data['other'][:,1]])
        bass = np.array([spleeter_data['bass'][:,0], spleeter_data['bass'][:,1]])
        drums = np.array([spleeter_data['drums'][:,0], spleeter_data['drums'][:,1]])
        spleeter_data = np.array([vocals, other, bass, drums])

        #sample down to FPS of visualization
        vis_data = self.sample_down(spleeter_data)

        #vis_data = self.apply_temp_blur(vis_data) - this feature is not yet used


        #normalization to fit into [0 ... 255] RGB value spectrum for each individual part with:
        vis_data = self.normalize(vis_data)
        
        #initialize array of vis_samples
        visualization = np.array([["0X000000" for j in range(self.NUM_PIXELS)] for k in range(self.len_vis)])

        for i in range(self.len_vis):

            visualization[i][0] = rgb_to_hex(0, 0, vis_data[0][0][i])
            visualization[i][1] = rgb_to_hex(0, vis_data[1][0][i], vis_data[1][0][i])
            visualization[i][2] = rgb_to_hex(0, vis_data[2][0][i], 0)
            visualization[i][3] = rgb_to_hex(vis_data[3][0][i], 0, 0)
            visualization[i][4] = rgb_to_hex(vis_data[3][1][i], 0, 0)
            visualization[i][5] = rgb_to_hex(0, vis_data[2][1][i], 0)
            visualization[i][6] = rgb_to_hex(0, vis_data[1][1][i], vis_data[1][1][i])
            visualization[i][7] = rgb_to_hex(0, 0, vis_data[0][1][i])

        #array of 300 processed vis_samples
        return visualization


        #self.prev_vis_data = vis_data - used for temporal bluring
        



    #Updating-Normalization-Factor-Finding-Function that always adjusts to highest observed value in each session, starting with normfac_init
    def update_norm_factor(self, k, max):
        if self.norm_factors[k]*max > self.max_rgb:
            self.norm_factors[k] = self.max_rgb/max

    #normalization function
    def normalize(self, vis_data):
        for k in range(4):



            self.update_norm_factor(k, np.amax(vis_data[k]))
            vis_data[k] = vis_data[k] * self.norm_factors[k]
        return vis_data

    #tempural blurring
    def apply_temp_blur(self, vis_data):
        # iterate through audio channels
        for k in range(4):
            # iterate through r/l:
            for j in range(2):
                # iterate through visual samples
                    for i in range(self.len_vis):
                            #temporal blurring
                            if i > 0:    
                                if vis_data[k][j][i-1] > vis_data[k][j][i]:
                                    vis_data[k][j][i] = vis_data[k][j][i-1]*0.8
                            if i == 0:
                                if self.prev_vis_data[k][j][self.len_vis-1] > vis_data[k][j][i]:
                                    vis_data[k][j][i] = self.prev_vis_data[k][j][self.len_vis-1]*0.8

        return vis_data

    #downsampling from audio RATE to visualization FPS
    def sample_down(self, spleeter_data):
        vis_data = np.array([[[0 for i in range(self.len_vis)] for j in range(2)] for k in range(4)])
        # iterate through audio channels
        for k in range(4):
            # iterate through r/l:
            for j in range(2):
                # iterate through visual samples
                    for i in range(self.len_vis):
                        # first need to check if there is anything nonzero
                        if np.any(spleeter_data[k][j][int(i*self.r_down):int((i+1)*self.r_down-1)]):
                            # to then find the maximum. this is a vis_sample
                            vis_data[k][j][i] = int(np.max(spleeter_data[k][j][int(i*self.r_down):int((i+1)*self.r_down-1)]))
        #array of 300 raw vis_samples
        return vis_data





