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
        self.prev_bass_sums = []
        max_key = math.floor(freq_to_piano_key(self.RATE/2))
        if max_key >= 142:
            print("max key is greater eq 120. it's: " + str(max_key))
            print("fftWorker initialized")

    def fftWorker(self, audiosample):
        frequency_dist = np.array([0 for j in range(142)], dtype=float) # wir gehen davon aus, dass max_key < 120
        time_begin = tm.perf_counter()
        fft_data = scipy.fftpack.rfft(audiosample)
        frequency_dist, self.prev_bass_sums = map_fft_to_freq_dist(self.RATE, audiosample, frequency_dist, fft_data, self.prev_bass_sums)
        time_end = tm.perf_counter()
        print("fftWorker time: " + str(time_end - time_begin))
        return frequency_dist

@numba.jit(nopython=True)
def freq_to_piano_key(freq):
    key = 12 * np.log2(freq/440) + 49
    if key < 0:
        key = 0
        print("key was smaller than 0, that really shouldnt happpen /: 'twas: " + str(key))
    return round(key)

@numba.jit(nopython=True)
def piano_key_to_freq(key):
    #if key < 50:
    #    return key * 10
    freq = 440 * np.power(2, (key-49)/12)
    return freq


#@numba.jit(nopython=True)
def map_fft_to_freq_dist(RATE, audiosample, frequency_dist, fft_data, prev_bass_sums):
    step = RATE/len(audiosample)
    
    for j in range(frequency_dist.size):

        if j < 51:
            freq = j
            next_freq = j + 1
            
            chunk = fft_data[freq:next_freq]
            if j>=35 and j<43:
                chunk = 1.2*chunk
            if j>=43 and j<48:
                chunk = 1.3*chunk
            if j>=48:
                chunk = 1.5*chunk
        else:
            freq = piano_key_to_freq(j)
            next_freq = piano_key_to_freq(j + 1)
            chunk = fft_data[int(freq/step):int(next_freq/step)]
            if j < 55:
                chunk = 0.85*chunk
            if j >=55 and j <= 58:
                chunk = 0.9*chunk
            if j >=58 and j <= 62:
                chunk = 0.95*chunk 
        value = 0
        if np.any(chunk):
            chunk = np.abs(chunk)
            value = np.sum(chunk)

        if j > 10:
            frequency_dist[j] = value
        else:
            frequency_dist[j] = 0

    bass_sum = np.max(frequency_dist[0:40])
    if len(prev_bass_sums) < 5000:
        prev_bass_sums.append(bass_sum)
    else:
        prev_bass_sums.pop(0)
        prev_bass_sums.append(bass_sum)


    #normalization to 0...1
    start = 0
    stop = frequency_dist.size
    frequency_dist[start:stop] = normalize(frequency_dist[start:stop])

#    if bass_sum > 2*np.mean(prev_bass_sums):
#        frequency_dist[0:20] += np.mean(frequency_dist[0:40]) + 0.5
#        print("got triggered")
        
    return frequency_dist, prev_bass_sums

@numba.jit(nopython=True)
def normalize(frequency_dist):
    if np.any(frequency_dist):
        max_value = np.max(frequency_dist)
        if max_value != 0:
            frequency_dist = frequency_dist*1/max_value
    return frequency_dist
