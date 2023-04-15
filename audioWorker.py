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


    def audioWorker(self, byte_data):
        print("audioWorker started!")
        #performance counter to see how fast our entire data processing is
        time_begin = tm.perf_counter()
        
        np_data = np.frombuffer(byte_data, dtype=np.int16)
        CHUNKSIZE = int(self.RATE/self.RATE_INTENSITY) #????? this might be wrong
        ##waveform_mono = np_data
        waveform_left = np_data
        waveform_right = np_data
        #waveform = np.reshape(np_data, (CHUNKSIZE, 2))
        #waveform_left = waveform[:,0]
        #waveform_right = waveform[:,1]
        #calculate normalized frequency distribution
        frequency_dist_left = self.fft_processor.fftWorker(waveform_left)
        #frequency_dist_right = self.fft_processor.fftWorker(waveform_right)
        #visualize
        visualization_left = self.visual_processor.visualize(waveform_left, frequency_dist_left)
        #visualization_right = self.visual_processor.visualize(waveform_right, frequency_dist_right)
        visualization_right = visualization_left
        #display performance
        time_end = tm.perf_counter()
        print("audioWorker time: " + str(time_end - time_begin))
        return visualization_left, visualization_right

    
