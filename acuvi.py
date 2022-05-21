
import multiprocessing
from multiprocessing import Process, Queue
import time as tm
import numpy as np
import audioIO
import separated_data
import file_visualizer
from audioWorker import audioWorker


stream_flag = 0 #this will be used to eventually exit the program! maybe... someday
framelength = 10 #size of rotating array to store audio and visual data (buffer of ~4 is necessary, so we use 10)
audio_output_counter = 0 #number of chunk when it gets out, corresponds to position in vis_frame
audio_input_counter = 0 #number of chunk when audio gets in

#experimental value that works for me
delay = 0.4

#basic settings (program might still break when changing these)
RATE=44100
CHUNKTIME = 10
CHUNKSIZE = RATE*CHUNKTIME
FPS = 30
NUM_PIXELS = 300
data_buffer = separated_data.separated_data_buffer()
#vis_frame is a rotating array of size 10, in which the vis_samples are stored in chunks of size FPS*CHUNKTIME
vis_frame = np.array([[["0x000000" for j in range(NUM_PIXELS)] for k in range(FPS*CHUNKTIME)] for l in range(framelength)])




def main():
    #necessary to prevent multiprocessing from taking over:
    multiprocessing.freeze_support()

    #these queues are necessary to send and receive data across processes (they are special multiprocessing queues)
    audio_in_queue = Queue()
    audio_out_queue = Queue()
    output_start_time = Queue()

    #initialize audio IO
    audio_io = audioIO.AudioIO(RATE, CHUNKTIME, CHUNKSIZE, framelength, audio_in_queue, audio_out_queue, output_start_time)
    #start IO process (it will create input and output audio streams)
    audio_io_worker = Process(target=audio_io.ioWorker, args=())
    audio_io_worker.start()

    #start spleeter and visualization process
    audio_worker = Process(target=audioWorker, args=(audio_in_queue, audio_out_queue,data_buffer, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS))
    audio_worker.start()
    #we wait until audio output has started to get initial audio output start time
    while(output_start_time.empty()):
        tm.sleep(0.5)
    initial_output_start_time = output_start_time.get()
    visualizer = file_visualizer.visualizer(RATE,data_buffer,initial_output_start_time)
    vis_worker = Process(target=visualizer.visualize(), args=())
    vis_worker.start()


#somehow necessary i dont know python
if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
