import sys
import wave
from typing import List

import numpy as np
import pyaudio
from scipy.io import wavfile

#reads the wav files and stores the data into a dictonary
samplerate, dataVocals = wavfile.read('vocals.wav')
print("vocals read:")
samplerate, dataBass = wavfile.read('bass.wav')
print("bass read:")
samplerate, dataDrums = wavfile.read('drums.wav')
print("drums read:")
samplerate, dataOther = wavfile.read('other.wav')
print("others read:")
data = [dataVocals.tolist(), dataBass.tolist(), dataDrums.tolist(), dataOther.tolist()]
print("data stored")





#returns the data from sample position to position+frames in a list and returns position aswell
def getFrames(frames: int,position: int):
    vocals = []
    bass = []
    drums = []
    other = []
    #print(position)
    for i in range(position, min(position+frames,len(data[0]))):
        vocals.append((data[0][i][0]/32768)*128)
        bass.append((data[1][i][0]/32768)*128)
        drums.append((data[2][i][0]/32768)*128)
        other.append((data[3][i][0]/32768)*128)
    position = position + frames
    return [vocals, bass, drums, other], position










