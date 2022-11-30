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
        max_key = math.floor(freq_to_piano_key(self.RATE/2))
        if max_key >= 142:
            print("max key is greater eq 120. it's: " + str(max_key))
            print("fftWorker initialized")

    def fftWorker(self, audiosample):
        frequency_dist = np.array([0 for j in range(142)], dtype=float) # wir gehen davon aus, dass max_key < 120
        time_begin = tm.perf_counter()
        fft_data = scipy.fftpack.rfft(audiosample)
        frequency_dist = map_fft_to_freq_dist(self.RATE, audiosample, frequency_dist, fft_data)
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


@numba.jit(nopython=True)
def map_fft_to_freq_dist(RATE, audiosample, frequency_dist, fft_data):
    step = RATE/len(audiosample)
    
    for j in range(frequency_dist.size):

        if j < 51:
            freq = j
            next_freq = j + 1
            chunk = fft_data[freq:next_freq]
        else:
            freq = piano_key_to_freq(j)
            next_freq = piano_key_to_freq(j + 1)
            chunk = fft_data[int(freq/step):int(next_freq/step)]

        value = 0
        if np.any(chunk):
            chunk = np.abs(chunk)
            value = np.sum(chunk)
        if j < 10:
            frequency_dist[j] = 0
        else:
            frequency_dist[j] = value

    #normalization to 0...1
    start = 0
    stop = frequency_dist.size
    frequency_dist[start:stop] = normalize(frequency_dist[start:stop])
    return frequency_dist

@numba.jit(nopython=True)
def normalize(frequency_dist):
    if np.any(frequency_dist):
        max_value = np.max(frequency_dist)
        if max_value != 0:
            frequency_dist = frequency_dist*1/max_value
    return frequency_dist