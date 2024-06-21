
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
RATE_INTENSITY = 147
RATE_FREQUENCY = 147
CHUNKSIZE = RATE/RATE_INTENSITY
NUM_PIXELS = 200
empty_color_val = "0x000000" #LED Leiste
empty_color_val_display = "#%02x%02x%02x" % (0, 0, 0) #RGBdisplay
arraysize = 50

def transformVis(smol_visualization, fast_visualization, visualization):
    # highs / inner ring
    for j in range(16):
        for k in range(3):
            for l in range(50):
                if l >= 20:
                    smol_visualization[54 + j][k] += (1/20)*float(fast_visualization[80 + l][k])*float(l)/20
                else:
                    smol_visualization[54 + j][k] += (1/20)*float(fast_visualization[80 + l][k])
    # middle: 30-42
    for j in range(22):
        for k in range(3):
            for l in range(70):
                if l < 10:
                    smol_visualization[31 +  j][k] += (1/5)*float(visualization[30 + l][k])*float(l - 10)/10
                elif l >= 20 and l < 50:
                    smol_visualization[31 +  j][k] += (1/5)*float(visualization[30 + l][k])
                elif l > 50:
                    smol_visualization[31 +  j][k] += (1/5)*float(visualization[30 + l][k])*float(70 - l)/10

    # outer ring: 1 - 27
    for j in range(27):
        for k in range(3):
            for l in range(60):
                if l < 40:
                    smol_visualization[1 + j][k] += (1/10)*float(visualization[l][k])
                else:
                    smol_visualization[1 + j][k] += (1/10)*float(visualization[l][k])*float(60 - l)/20

    return smol_visualization

def main():
    #necessary to prevent multiprocessing from taking over:
    multiprocess.freeze_support()

    #these queues are necessary to send and receive data across processes (they are special multiprocessing queues)
    audio_in_queue = Queue()
    audio_out_queue = Queue()
    #start visualization process
    audio_processor = audioWorker.audioWorkerino(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)
    fast_audio_processor = audioWorker.audioWorkerino(RATE, RATE_INTENSITY, RATE_FREQUENCY, NUM_PIXELS)

    #initialize audio IO
    audio_in = audioIn.AudioIn(RATE, RATE_INTENSITY, audio_in_queue, audio_out_queue)
    #start IO process (it will create input and output audio streams)
    audio_in_worker = Process(target=audio_in.audioInWorker, args=())
    audio_in_worker.start()
    

    
    if mode == 0:
        #imports need to be here because of bug in libusb device access
        #initialization of LEDs via USB SPI chip
        import board
        import neopixel
        LED_PIN = board.D18
        LED_COUNT = 71
        PIXEL_ORDER = neopixel.GRB
        pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness = 1, pixel_order=PIXEL_ORDER, auto_write=False)

    else:
        import rgbDisplay
        RGB = rgbDisplay.RGB_display(12, 4)
        RGB.createRgbDisplay()

    #start the visualization loop
    visualization_left = np.array([[0 for i in range(3)] for i in range(NUM_PIXELS)])
    visualization_right = np.array([[0 for i in range(3)] for i in range(NUM_PIXELS)])

    last_audiosamples = np.zeros((int(CHUNKSIZE * arraysize),))
    #print(last_audiosamples)
    rotary_idx = 0
    list_init = False

    while True: 
        try:
            #get visual data from processing queue
            while audio_in_queue.empty():
                tm.sleep(0.0005)
            
            while list_init == False:
                while audio_in_queue.empty():
                    tm.sleep(0.0005)
                byte_data = audio_in_queue.get()
                np_data = np.frombuffer(byte_data, dtype=np.int16)
                last_audiosamples[ : int((arraysize - 1) * CHUNKSIZE)] = last_audiosamples[int(CHUNKSIZE) : ]
                last_audiosamples[int((arraysize - 1) * CHUNKSIZE) : ] = np_data
                rotary_idx += 1
                if rotary_idx == (arraysize - 1):
                    list_init = True
            counter = 0
            while not audio_in_queue.empty():
                counter += 1
                byte_data = audio_in_queue.get()
                if counter > 1:
                    print("overrun!!")

            np_data = np.frombuffer(byte_data, dtype=np.int16)
            print("AUDIO DATA: ")
            print(np_data)
            print("MEAN:")
            print(np.mean(np_data))
            last_audiosamples[ : int((arraysize - 1) * CHUNKSIZE)] = last_audiosamples[int(CHUNKSIZE) : ]
            last_audiosamples[int((arraysize - 1) * CHUNKSIZE) : ] = np_data


            visualization  = audio_processor.audioWorker(last_audiosamples[int((arraysize - 50) * CHUNKSIZE) : ])
            fast_visualization = fast_audio_processor.audioWorker(last_audiosamples[int((arraysize - 10) * CHUNKSIZE) : ])
            """for i in range(len(visualization_left)):
                for k in range(3):
                    mean = (visualization_left[i][k] + visualization_right[i][k])/2
                    if (visualization_left[i][k] - visualization_right[i][k]) > 0:
                        visualization_left[i][k] = 2 * (visualization_left[i][k] - visualization_right[i][k])
                    if (visualization_right[i][k] - visualization_left[i][k]) > 0:
                        visualization_right[i][k] = 2 * (visualization_right[i][k] - visualization_left[i][k])"""
            if mode == 0:
                time_begin = tm.perf_counter()
                smol_visualization = np.zeros((71, 3), dtype=float)
                lightmode = "background"
                if lightmode == "background":
                    """for i in range(4):
                        for j in range(11):
                            for k in range(3):
                                smol_visualization[2 + j][k] += float(visualization[3*12 + j + i*12][k])
                                smol_visualization[20 + j][k] += float(visualization[3*12 + j + i*12][k])

                    for j in range(12):
                        for k in range(3):
                            smol_visualization[18][k] += float(visualization[j][k])
                    for j in range(12):
                        for k in range(3):
                            smol_visualization[17][k] += float(visualization[12+j][k])
                            smol_visualization[19][k] += float(visualization[12+j][k])
                    
                
                    for j in range(13):
                        for k in range(3):
                            smol_visualization[14] += float(fast_visualization[100 + j][k])/10
                            smol_visualization[33] += float(fast_visualization[100 + j][k])/10
                        
                    for j in range(13):
                        for k in range(3):
                            smol_visualization[15] += float(fast_visualization[113 + j][k])/10
                            smol_visualization[34] += float(fast_visualization[113 + j][k])/10
                    for j in range(13):
                        for k in range(3):
                            smol_visualization[16] += float(fast_visualization[126 + j][k])/10
                            smol_visualization[35] += float(fast_visualization[126 + j][k])/10"""
                    # 0 is just repeater
                    # first interval: 54-70
                    smol_visualization = transformVis(smol_visualization, fast_visualization, visualization)
                if lightmode == "concert":
                    for i in range(14):
                        for j in range(10):
                            for k in range(3):
                                smol_visualization[i][k] += float(visualization[10 * i + j][k])/2
                else: 
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

                for i in range(71):
                    hex_val = rgb_to_hex(visualization[i][0], visualization[i][1], visualization[i][2])
                    pixels[i] = int(hex_val, 16)
                time_end = tm.perf_counter()
                print("main loops time: " + str(time_end - time_begin))
                print("before calling pixels.show()")
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
