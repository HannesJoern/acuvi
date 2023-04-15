
import multiprocess
from multiprocess import Process, Queue
import time as tm
import numpy as np
import math
from sharedFunctions import *
import audioIn
import audioWorker

mode = 0 # 1 = rgb display, 0 = LEDs

#basic settings (program might still break when changing these)
RATE=44100
RATE_INTENSITY = 60
RATE_FREQUENCY = 60

NUM_PIXELS = 141
empty_color_val = "0x000000" #LED Leiste
empty_color_val_display = "#%02x%02x%02x" % (0, 0, 0) #RGBdisplay


def main():
    #necessary to prevent multiprocessing from taking over:
    multiprocess.freeze_support()

    #these queues are necessary to send and receive data across processes (they are special multiprocessing queues)
    audio_in_queue = Queue()

    #start visualization process
    audio_processor = audioWorker.audioWorkerino(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)

    #initialize audio IO
    audio_in = audioIn.AudioIn(RATE, RATE_INTENSITY, audio_in_queue)
    #start IO process (it will create input and output audio streams)
    audio_in_worker = Process(target=audio_in.audioInWorker, args=())
    audio_in_worker.start()
    

    
    if mode == 0:
        #imports need to be here because of bug in libusb device access
        #initialization of LEDs via USB SPI chip
        import board
        import neopixel_spi as neopixel
        PIXEL_ORDER = neopixel.GRB
        spi = board.SPI()
        pixels = neopixel.NeoPixel_SPI(spi, 16, brightness = 1, pixel_order=PIXEL_ORDER, auto_write=False)

    else:
        import rgbDisplay
        RGB = rgbDisplay.RGB_display(12, 4)
        RGB.createRgbDisplay()

    #start the visualization loop
    visualization_left = np.array([[0 for i in range(3)] for i in range(NUM_PIXELS)])
    visualization_right = np.array([[0 for i in range(3)] for i in range(NUM_PIXELS)])
    while True: 
        try:
            #get visual data from processing queue
            while audio_in_queue.empty():
                tm.sleep(0.005)
            while not audio_in_queue.empty():
                byte_data = audio_in_queue.get()

            visualization_left, visualization_right = audio_processor.audioWorker(byte_data)
            
            """for i in range(len(visualization_left)):
                for k in range(3):
                    mean = (visualization_left[i][k] + visualization_right[i][k])/2
                    if (visualization_left[i][k] - visualization_right[i][k]) > 0:
                        visualization_left[i][k] = 2 * (visualization_left[i][k] - visualization_right[i][k])
                    if (visualization_right[i][k] - visualization_left[i][k]) > 0:
                        visualization_right[i][k] = 2 * (visualization_right[i][k] - visualization_left[i][k])"""
            if mode == 0:
                smol_visualization = np.zeros((48, 3), dtype=float)
                for i in range(5):
                    for j in range(11):
                        for k in range(3):
                            smol_visualization[j][k] += float(visualization_left[3*12 + i*12 + j][k])/2
                for i in range(5):
                    for j in range(11):
                        for k in range(3):
                             pass
                            #smol_visualization[12 + j][k] += float(visualization_right[3*12 + i*12 + j][k])/2


                for i in range(3):
                    for j in range(11):
                        for k in range(3):
                            pass
                            #smol_visualization[12 + j][k] += float(visualization_left[i*12 + j][k])
                for i in range(4):
                    for j in range(11):
                        for k in range(3):
                            pass
                            #smol_visualization[12 + round(0.5*j)][k] += float(visualization_left[8*12 + i + j*4][k])
                #write vis_sample to LEDs
                visualization = smol_visualization
                for i in range(16):
                    hex_val = rgb_to_hex(visualization[i][0], visualization[i][1], visualization[i][2])
                    pixels[i] = int(hex_val, 16)
                
                pixels.show()
            else:
                #hex_display_vals = np.array([empty_color_val_display for h in range(300)])
                smol_visualization = np.zeros((48, 3), dtype=float)
                for i in range(5):
                    for j in range(11):
                        for k in range(3):
                            smol_visualization[24 + j][k] += float(visualization_left[3*12 + i*12 + j][k])/2
                for i in range(5):
                    for j in range(11):
                        for k in range(3):
                            smol_visualization[12 + j][k] += float(visualization_right[3*12 + i*12 + j][k])/2
                

                for i in range(3):
                    for j in range(11):
                        for k in range(3):
                            smol_visualization[36 + j][k] += float(visualization_left[i*12 + j][k])
                for i in range(4):
                    for j in range(11):
                        for k in range(3):
                            smol_visualization[j][k] += float(visualization_left[8*12 + i + j*4][k])
                """for k in range(3):
                    smol_visualization[15][k] = np.sum(visualization[100:140][0])"""
                """for i in range(20):
                    for j in range(7):
                        for k in range(3):
                            smol_visualization[i][k] += float(visualization[i*7 + j][k])/7"""
                visualization = smol_visualization
                hex_display_vals = np.array([empty_color_val_display for h in range(48)])
                for i in range(48):
                    if i < NUM_PIXELS:
                        hex_display_vals[i] = rgb_to_hex_display(int(visualization[i][0]), int(visualization[i][1]), int(visualization[i][2]))
                    else: 
                        hex_display_vals[i] = rgb_to_hex_display(0, 0, 0)
                RGB.colorSquares(hex_display_vals)
                
                """for i in range(300):
                    if i < NUM_PIXELS:
                        hex_display_vals[i] = rgb_to_hex_display(visualization[i][0], visualization[i][1], visualization[i][2])
                    else: 
                        hex_display_vals[i] = rgb_to_hex_display(0, 0, 0)
                RGB.colorSquares(hex_display_vals)"""
                RGB.update()
                #plt.plot(visualization)
                #plt.show()

        #this was intended to exit the program but doesnt work
        except KeyboardInterrupt:
            audio_in.terminate()

#somehow necessary i dont know python
if __name__ == '__main__':
    multiprocess.freeze_support()
    main()
