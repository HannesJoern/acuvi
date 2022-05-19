from spleeter.separator import Separator
import numpy as np
import time as tm

class AudioProcessor:
    def __init__(self, RATE, CHUNKSIZE, CHUNKTIME):
        self.separator = Separator('spleeter:4stems')
        self.RATE = RATE
        self.CHUNKSIZE = CHUNKSIZE
        self.CHUNKTIME = CHUNKTIME

    def separate(self, in_data):
        time_begin = tm.perf_counter()
        byte_data = in_data
        np_data = np.frombuffer(byte_data, dtype=np.int16)
        waveform = np.reshape(np_data, (self.CHUNKSIZE, 2))
        prediction = self.separator.separate(waveform) 
        time_end = tm.perf_counter()
        print("time for separate: " + str(time_end - time_begin))

        return prediction

    #destructor missing!!