import numpy as np
#@numba.jit
def freq_to_piano_key(freq):
    key = 12 * np.log2(freq/440) + 49
    if key < 0:
        key = 0
        print("key was smaller than 0, that really shouldnt happpen /: 'twas: " + str(key))
    return round(key)

#@numba.jit
def piano_key_to_freq(key):
    freq = 440 * np.power(2, (key-49)/12)
    return freq

for i in range(143):
    print(i)
    print(piano_key_to_freq(i)/10)
    if piano_key_to_freq(i)/10 > i:
        print("yes")
#@numba.jit
def map_fft_to_freq_dist(RATE, audiosample, frequency_dist, fft_data):
    step = RATE/len(audiosample)
    for j in range(frequency_dist.size):
        freq = piano_key_to_freq(j)
        next_freq = piano_key_to_freq(j + 1)
        chunk = fft_data[int(freq/step):int(next_freq/step)]
        value = 0
        if np.any(chunk):
            value = np.sum(chunk)
        frequency_dist[j] = value
    return frequency_dist