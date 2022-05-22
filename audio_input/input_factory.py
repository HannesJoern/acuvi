from tkinter import S
import input_audio
from audio_buffer import audio_buffer
import youtube_stream
import pathlib

#this function returns an object that is responsible for providing the input audio to be separated and visualized
def factory(input_type = 'stream',SAMPLERATE = 'deafult',CHUNKSIZE = 'deafult', input_device_index = 'deafult'):
    if input_type == 'stream':
        return input_audio.input_stream(audio_buffer=audio_buffer(),SAMPLERATE=SAMPLERATE, CHUNKSIZE=CHUNKSIZE, input_device_index=input_device_index)
    if input_type == 'youtube' or 'yt':
        return youtube_stream.youtube_stream(str(pathlib.Path(__file__).parent.resolve()))