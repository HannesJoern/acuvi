import pyaudio
import time as tm


class AudioIO:
    def __init__(self, RATE, CHUNKTIME, CHUNKSIZE, framelength, audio_in_queue, audio_out_queue, output_start_time):
        self.audio_input_counter = 0 #this starts at zero and with each audio input it gets increased by 1, then it gets cut of above 10 with (% 10) to make the array rotate
        self.RATE = RATE
        self.CHUNKTIME = CHUNKTIME
        self.CHUNKSIZE = CHUNKSIZE
        self.framelength = framelength
        self.audio_in_queue = audio_in_queue
        self.audio_out_queue = audio_out_queue
        self.output_start_time = output_start_time


    def ioWorker(self):
        #pyaudio automatically chooses default devices and creates stream in callback mode
        pIn = pyaudio.PyAudio()
        pOut = pyaudio.PyAudio()
        streamIn = pIn.open(format=pyaudio.paInt16, channels=2, rate=self.RATE, input=True, stream_callback=self.callbackIn, frames_per_buffer=self.CHUNKSIZE)
        streamOut = pOut.open(format=pyaudio.paInt16, channels=2, rate=self.RATE, output=True, stream_callback=self.callbackOut, frames_per_buffer=self.CHUNKSIZE)

        #start recording audio
        streamIn.start_stream()

        #wait until processor is done with first chunk of data


        #start audio output stream
        streamOut.start_stream()

        #record timestamp
        initial_output_start_time = tm.time()
        #give timestamp to display so it can synchronize
        self.output_start_time.put(initial_output_start_time)

        while(True):
            tm.sleep(0.5)

        #again - destructor is not reachable! please exit the program with force

    #function called by pyaudio stream whenever it gets new data
    def callbackIn(self, in_data, frame_count, time_info, status):
    
        self.audio_in_queue.put((in_data, self.audio_input_counter))
        print('audio input received with input counter: ' + str(self.audio_input_counter))
        self.audio_input_counter = (self.audio_input_counter + 1) % (self.framelength - 1)
        return (in_data, pyaudio.paContinue)


    #function called by pyaudio stream whenever it needs new data
    def callbackOut(self, in_data, frame_count, time_info, status):
        while self.audio_out_queue.empty():
            tm.sleep(0.05)
        
        data, output_counter = self.audio_out_queue.get()
        print("audio output sent with output counter:" + str(output_counter))
        
        return (data, pyaudio.paContinue)

