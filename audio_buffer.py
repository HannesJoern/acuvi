import numpy as np

class audio_buffer:
    def __init__(self,SAMPLERATE = -1) -> None:
        self.SAMPLERATE = SAMPLERATE
        self.audio_data = np.array()
    
    def put(self,audio_in):
        self.audio_data = np.append(self.audio_data,audio_in)

    def get(self,samples):
        to_return = self.audio_data[:samples]
        self.audio_data = self.audio_data[samples:]
        return to_return

    def set_samplerate(self,SAMPLERATE):
        self.SAMPLERATE = SAMPLERATE