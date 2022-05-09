import sys
import time as tm
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from multiprocess import Process, Queue
 
#fig, (ax1 , ax2, ax3, ax4)= plt.subplots(4)
fig, ax = plt.subplots()
#ax = fig.add_subplot()


#vis_data = np.array([[0 for i in range(300)] for i in range(4)])
time_new_chunk = tm.time()
delay = 0
vis_frame = np.array([[[0 for i in range(300)] for j in range(4)] for k in range(100)])
audio_output_counter = 0

def animate(i, mp_queue_vis, mp_queue_delay, RATE, CHUNKSIZE, CHUNKTIME, FPS):
    global time_new_chunk, vis_frame, delay, audio_output_counter


    while not mp_queue_vis.empty():
        vis_data, vis_counter = mp_queue_vis.get()
        vis_frame[vis_counter + 1] = vis_data
        print("vis data " + str(vis_counter) + " came in!")
        print(vis_data.shape)

    
    while not mp_queue_delay.empty():
        audio_output_time, audio_output_counter = mp_queue_delay.get()
        time_new_chunk = tm.time()
        delay = time_new_chunk - audio_output_time 
        print("delay data " + str(audio_output_counter) + " came in with delay: " + str(delay))

    #if np.max(vis_data) > 0:
    #   vis_data = vis_data/np.max(vis_data)

    #print()

   

    current_time = tm.time()
    experimental_delay_margin = 0
    position = math.floor((current_time - (time_new_chunk + delay) + experimental_delay_margin)*FPS) % FPS*CHUNKTIME
    if position < 0:
        position = 0
    
    ax.clear()
    ax.bar(0, vis_frame[audio_output_counter][0][position], width=1, edgecolor="white", linewidth=0.7)
    ax.bar(1, vis_frame[audio_output_counter][1][position], width=1, edgecolor="white", linewidth=0.7)
    ax.bar(2, vis_frame[audio_output_counter][2][position], width=1, edgecolor="white", linewidth=0.7)
    ax.bar(3, vis_frame[audio_output_counter][3][position], width=1, edgecolor="white", linewidth=0.7)
    ax.set(xlim=(0,4), ylim=(0,2000))
    #ax1.clear()
    #ax2.clear()
    #ax3.clear()
    #ax4.clear()

    #ax1.plot(vis_frame[audio_output_counter][0])
    #ax2.plot(vis_frame[audio_output_counter][1])
    #ax3.plot(vis_frame[audio_output_counter][2])
    #ax4.plot(vis_frame[audio_output_counter][3])
    #print("plot has been plotted with output counter: " + str(audio_output_counter))

def visOutput(mp_queue, mp_queue_vis, mp_queue_delay, RATE, CHUNKSIZE, CHUNKTIME, FPS):
    print("visoutput started!")
    ani = animation.FuncAnimation(fig, animate, fargs=(mp_queue_vis, mp_queue_delay, RATE, CHUNKSIZE, CHUNKTIME, FPS), interval=FPS)
    plt.show()