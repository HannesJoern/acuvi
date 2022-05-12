from typing import List

import pyaudio
import wave
import os


def openStream(frames):
    device_info = {}

    # Use module
    p = pyaudio.PyAudio()

    # Set default to first in list or ask Windows
    try:
        default_device_index = p.get_default_input_device_info()
    except IOError:
        default_device_index = -1

    # Get device info
    try:
        device_info = p.get_device_info_by_index(5)
    except IOError:
        device_info = p.get_device_info_by_index(default_device_index)

    # Open stream
    channelcount = device_info["maxInputChannels"] if (
                device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info[
        "maxOutputChannels"]
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=int(device_info["defaultSampleRate"]),
                    input=True,
                    frames_per_buffer=frames,
                    input_device_index=device_info["index"],
                    as_loopback=True)
    return stream, p

def generateFile(frames: int, stream: pyaudio.Stream):

    recorded_frames = []

    #recorded_frames.append(stream.read(frames))

    #print(frames)
    #print(len(recorded_frames))


    return mergeBytes(stream.read(frames))

def close(stream: pyaudio.Stream , p) :
    stream.stop_stream()
    stream.close()

    # Close module
    p.terminate()

def mergeBytes(lista):
    result = []
    for i in range(int(len(lista)/2)):
        #result.append((lista[i*2] << 8)+lista[(i*2)+1])
        result.append(int.from_bytes(byteorder="little",signed=True,bytes=[lista[i*2],lista[(i*2)+1]]))
    return result