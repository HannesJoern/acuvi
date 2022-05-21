import pyaudio
import numpy as np

class input_stream:

    #this class creates an input stream with device with index "input_device_index" with the given samplerate and chunksize, if nothing is given the deafult device with the deafult
    #samplerate and cunksize of 1024 is used
    def __init__(self,audio_buffer,SAMPLERATE = 'deafult',CHUNKSIZE = 'deafult', input_device_index = 'deafult'):
        self.p = pyaudio.PyAudio()
        self.audio_buffer = audio_buffer
        #if nothing is given as the index the deafult input device is used, else the input device with the given index is selected
        devinfo = self.p.get_default_input_device_info() if input_device_index =='deafult' else self.p.get_device_info_by_index(input_device_index) 
        self.SAMPLERATE = devinfo['deafultSampleRate'] if SAMPLERATE == 'deafult' else SAMPLERATE
        self.CHUNKSIZE = 1024 if CHUNKSIZE == 'deafult' else CHUNKSIZE
        self.audio_buffer.set_samplerate(self.SAMPLERATE)
        self.input_stream = self.p.open(format = pyaudio.paInt16,
                                        channels = 2,
                                        input_device_index = devinfo['index'],
                                        rate= self.SAMPLERATE,
                                        frames_per_buffer = self.CHUNKSIZE,
                                        stream_callback=self.callback,
                                        input = True)
    
    #starts the stream
    def start_stream(self):
        self.input_stream.start_stream()

    #closes the stream
    def close_stream(self):
        self.input_stream.stop_stream()
        self.input_stream.close()
        self.p.terminate()

    #returns with 'sample_count' as format a list with length "length" is returned, with 'seconds' as format a list with the contens of "length" seconds of audio data is returned
    def get(self, length: float, format = 'sample_count'):
        if format == 'sample_count':
            return self.mergeBytes(self.input_stream.read(int(length)))
        if format == 'seconds':
            return self.mergeBytes(self.input_stream.read(int(length*self.SAMPLERATE)))

    #helper function to transform byte data to an int list
    def mergeBytes(lista):
        result = []
        for i in range(int(len(lista)/2)):
            result.append(int.from_bytes(byteorder="little",signed=True,bytes=[lista[i*2],lista[(i*2)+1]]))
        return result

    #this function is called every time samples with the length of CHUNKSIZE arrived, here the collected data is sent to a buffer, where the audio data is stored to be played afterwards
    def callback(self, in_data, frame_count, time_info, status):
        self.audio_buffer.put(self.mergeBytes(in_data))
        return (in_data, pyaudio.paContinue)