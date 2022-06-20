import time as tm
import numpy as np

import visualizer
from multiprocess import Process, Queue


def audioWorker(audio_in_queue, visual_data_queue, RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS, frequency_dist_queue, fft_audio_in_queue):
    print("audioWorker started!")

    waveform_for_fft = np.array([0 for i in range(int(RATE/RATE_FREQUENCY))])
    fft_data_counter = 0

    visual_processor = visualizer.Visualizer(RATE, RATE_INTENSITY, RATE_FREQUENCY, frequency_dist_queue, NUM_PIXELS)

    print("audioworker initialized successfully")
    while(True):
        #wait for callback-in function to deliver us new data
        while audio_in_queue.empty():
            tm.sleep(0.01)
            
        #performance counter to see how fast our entire data processing is
        time_begin = tm.perf_counter()
        
        #get data from audio input stream
        while not audio_in_queue.empty():
            byte_data = audio_in_queue.get()

        np_data = np.frombuffer(byte_data, dtype=np.int16)
        CHUNKSIZE = int(RATE/RATE_INTENSITY) #????? this might be wrong
        waveform = np.reshape(np_data, (CHUNKSIZE, 2))
        waveform_mono = waveform[:,0]

        waveform_for_fft[int(fft_data_counter*(RATE/RATE_INTENSITY)):int((fft_data_counter + 1)*RATE/RATE_INTENSITY)] = waveform_mono
        
        if fft_data_counter == 2:
            fft_audio_in_queue.put(waveform_for_fft)

        fft_data_counter = (fft_data_counter + 1) % int(RATE_INTENSITY/RATE_FREQUENCY)

        #visualize
        visualization = visual_processor.visualize(waveform_mono)

        #give visual data available to display
        visual_data_queue.put(visualization)

        #display performance
        time_end = tm.perf_counter()
    return

  
