import time as tm
import numpy as np

import visualizer
import fftWorker
from multiprocess import Process, Queue

class audioWorkerino:
    def __init__(self, RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS):
        self.waveform_for_fft = np.array([0 for i in range(int(RATE/RATE_FREQUENCY))])
        self.fft_data_counter = 0

        self.visual_processor = visualizer.Visualizer(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)
        self.fft_processor = fftWorker.fftWorkerino(RATE, RATE_FREQUENCY, NUM_PIXELS)
        self.RATE = RATE
        self.RATE_INTENSITY = RATE_INTENSITY
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS


    def audioWorker(self, waveform):
        #print("audioWorker started!")
        #performance counter to see how fast our entire data processing is
        time_begin = tm.perf_counter()
        
        CHUNKSIZE = int(self.RATE/self.RATE_INTENSITY) #????? this might be wrong

        #calculate normalized frequency distribution
        frequency_dist = self.fft_processor.fftWorker(waveform)
        #frequency_dist_right = self.fft_processor.fftWorker(waveform_right)
        #visualize
        visualization = self.visual_processor.visualize(waveform, frequency_dist)
        #visualization_right = self.visual_processor.visualize(waveform_right, frequency_dist_right)
        #display performance
        time_end = tm.perf_counter()
        #print("audioWorker time: " + str(time_end - time_begin))
        return visualization

    
