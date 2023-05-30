import scipy.fftpack
import numpy as np
from sharedFunctions import *
import math
import numba
import time as tm

class fftWorkerino:
    def __init__(self, RATE, RATE_FREQUENCY, NUM_PIXELS):
        self.RATE = RATE
        self.RATE_FREQUENCY = RATE_FREQUENCY
        self.NUM_PIXELS = NUM_PIXELS
        self.volume_history = np.zeros((2000,), dtype=np.float64)
        self.volume_history_pos = 0
        max_key = math.floor(freq_to_piano_key(self.RATE/2))
        if max_key < NUM_PIXELS:
            print("num pixels is bigger than max key")
        print("fftWorker initialized")

    def fftWorker(self, audiosample):
        frequency_dist = np.array([0 for j in range(self.NUM_PIXELS)], dtype=float) # wir gehen davon aus, dass max_key < 120
        time_begin = tm.perf_counter()
        fft_data = scipy.fftpack.rfft(audiosample)
        frequency_dist, self.volume_history, self.volume_history_pos = map_fft_to_freq_dist(self.RATE, audiosample, frequency_dist, fft_data, self.volume_history, self.volume_history_pos)
        time_end = tm.perf_counter()
        #print("fftWorker time: " + str(time_end - time_begin))
        return frequency_dist

@numba.jit(nopython=True)
def freq_to_piano_key(freq):
    #key = 12 * np.log2(freq/440) + 49
    key = 12 * np.log2((freq - 120)/440)
    if key < 0:
        key = 0
        print("key was smaller than 0, that really shouldnt happpen /: 'twas: " + str(key))
    return round(key)

@numba.jit(nopython=True)
def piano_key_to_freq(key):
    #if key < 50:
    #    return key * 10
    #freq = 440 * np.power(2, (key-49)/12)
    freq = 440 * np.power(2, (key-49)/12) + 120
    return freq


@numba.jit(nopython=True)
def map_fft_to_freq_dist(RATE, audiosample, frequency_dist, fft_data, volume_history, volume_history_pos):
    step = RATE/len(audiosample)
    
    for j in range(frequency_dist.size):

        freq = piano_key_to_freq(j)
        next_freq = piano_key_to_freq(j + 1)
        chunk = fft_data[int(freq/step):int(next_freq/step)] 
        value = 0
        if np.any(chunk):
            chunk = np.abs(chunk)
            value = np.sum(chunk)

        frequency_dist[j] = value


    #normalization to 0...1
    start = 0
    stop = frequency_dist.size
    frequency_dist[start:stop], volume_history, volume_history_pos = normalize(frequency_dist[start:stop], volume_history, volume_history_pos)


        
    return frequency_dist, volume_history, volume_history_pos

@numba.jit(nopython=True)
def normalize(frequency_dist, volume_history, volume_history_pos):
    if np.any(frequency_dist):
        max_value = np.max(frequency_dist)
        volume_history[volume_history_pos] = max_value
        mean_volume = np.mean(volume_history)
        if(mean_volume < 10000):
            frequency_dist = frequency_dist/10000
        else:
            frequency_dist = frequency_dist/mean_volume
        volume_history_pos += 1
        if volume_history_pos >= 2000:
            volume_history_pos = 0
    return frequency_dist, volume_history, volume_history_pos
