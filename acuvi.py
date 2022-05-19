
import multiprocess
from multiprocess import Process, Queue
import time as tm
import numpy as np
import math
from sharedFunctions import *
import audioIO

import matplotlib.pyplot as plt



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

#vis_frame is a rotating array of size 10, in which the vis_samples are stored in chunks of size FPS*CHUNKTIME
vis_frame = np.array([[["0x000000" for j in range(NUM_PIXELS)] for k in range(FPS*CHUNKTIME)] for l in range(framelength)])

from audioWorker import audioWorker


def main():
    #necessary to prevent multiprocessing from taking over:
    multiprocess.freeze_support()

    #imports need to be here because of bug in libusb device access
    #initialization of LEDs via USB SPI chip
    import board
    import neopixel_spi as neopixel

    PIXEL_ORDER = neopixel.GRB
    spi = board.SPI()

    pixels = neopixel.NeoPixel_SPI(spi, NUM_PIXELS, pixel_order=PIXEL_ORDER, auto_write=False)

    #these queues are necessary to send and receive data across processes (they are special multiprocessing queues)
    audio_in_queue = Queue()
    visual_data_queue = Queue()
    audio_out_queue = Queue()
    output_start_time = Queue()

    #initialize audio IO
    audio_io = audioIO.AudioIO(RATE, CHUNKTIME, CHUNKSIZE, framelength, audio_in_queue, audio_out_queue, visual_data_queue, output_start_time)
    #start IO process (it will create input and output audio streams)
    audio_io_worker = Process(target=audio_io.ioWorker, args=())
    audio_io_worker.start()

    #start spleeter and visualization process
    audio_worker = Process(target=audioWorker, args=(audio_in_queue, visual_data_queue, audio_out_queue, RATE, CHUNKSIZE, CHUNKTIME, FPS, NUM_PIXELS))
    audio_worker.start()

    #we wait until audio output has started to get initial audio output start time
    while(output_start_time.empty()):
        tm.sleep(0.5)
    initial_output_start_time = output_start_time.get()

    #start the visualization loop
    while True: 
        try:   
            #get visual data from processing queue
            while not visual_data_queue.empty():

                visualization, vis_counter = visual_data_queue.get()
                vis_frame[vis_counter + 1] = visualization
                print("vis data " + str(vis_counter) + " came in!")

            #calculate position in frame (audio_output_counter) and in chunk (position)
            current_time = tm.time()
            audio_output_counter = int(math.floor((current_time - initial_output_start_time) / 10) )
            position = int(((current_time + delay - initial_output_start_time) % 10) * FPS)

            #precaution in case of bugs
            if position < 0 or position > FPS*CHUNKTIME:
                print("position corrected to fit into array" + str(position))
                position = 0                         
            
            #obtain vis_sample
            vis_sample = vis_frame[audio_output_counter][position]
            
            #write vis_sample to LEDs
            for i in range(300):
                pixels[i] = int(vis_sample[i], 16)

            pixels.show()
            
        #this was intended to exit the program but doesnt work
        except KeyboardInterrupt:
            audio_io.terminate()
            audio_worker.join()


#somehow necessary i dont know python
if __name__ == '__main__':
    multiprocess.freeze_support()
    main()
