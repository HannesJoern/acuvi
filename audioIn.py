import pyaudio
import time as tm


class AudioIn:
    def __init__(self, RATE, RATE_INTENSITY, audio_in_queue):
        self.audio_input_counter = 0 #this starts at zero and with each audio input it gets increased by 1, then it gets cut of above framelength with (% framelength) to make the array rotate
        self.RATE = RATE
        self.audio_in_queue = audio_in_queue
        self.CHUNKSIZE = RATE/RATE_INTENSITY


    def audioInWorker(self):
        #pyaudio automatically chooses default devices and creates stream in callback mode
        pIn = pyaudio.PyAudio()

        streamIn = pIn.open(format=pyaudio.paInt16, channels=2, rate=self.RATE, input=True, stream_callback=self.callbackIn, frames_per_buffer=int(self.CHUNKSIZE))

        #start recording audio
        streamIn.start_stream()

        while(True):
            tm.sleep(0.5)

        #again - destructor is not reachable! please exit the program with force
        self.streamIn.stop_stream()
        self.streamIn.close()
        self.pIn.terminate()

    #function called by pyaudio stream whenever it gets new data
    def callbackIn(self, in_data, frame_count, time_info, status):
        self.audio_in_queue.put((in_data))
        return (in_data, pyaudio.paContinue)