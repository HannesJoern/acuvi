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
        waveform_mono = np_data
       # waveform = np.reshape(np_data, (CHUNKSIZE, 2))
       # waveform_mono = waveform[:,0]
        #calculate normalized frequency distribution
        frequency_dist = self.fft_processor.fftWorker(waveform_mono)
        #visualize
        visualization = self.visual_processor.visualize(waveform_mono, frequency_dist)

        #display performance
        time_end = tm.perf_counter()
        print("audioWorker time: " + str(time_end - time_begin))
        return visualization

    
