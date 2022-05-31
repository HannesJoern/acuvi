
import time
import pygame
import RGB_display
from control_window import control_window
import wav_4_stems
import sys
import visualizer
import itertools

args = sys.argv
path = args[1]
name = args[2]
wav_data = wav_4_stems.wav_4_stems(path + "\\separated_files\\" + name)
rgb = RGB_display.RGB_display(75,4)
rgb.createRgbDisplay()
position = 0
secondsPerFrame = 1/(wav_data.samplerate/1536)
control_window = control_window()
pygame_paused = False
pygame.mixer.init()
s = pygame.mixer.Sound(path + "\\wav_files\\" + name + ".wav")
s.play()
start_time = time.time()
vis = visualizer.visualizer()
while True:
    timer = time.time()
    if not control_window.ispaused: 
        data, pos = wav_data.getFrames(frames=1536, position=int((timer-start_time)*wav_data.samplerate))
        voice = data[0]
        bass = data[1]
        drums = data[2]
        other = data[3]
        if pygame_paused:
            print("unpaused")
            pygame.mixer.unpause()
            pygame_paused = False
    else:
        voice = [0]*1536
        bass = [0]*1536
        drums = [0]*1536
        other = [0]*1536
        if not pygame_paused:
            print("paused")
            pygame.mixer.pause()
            pygame_paused = True
    if len(drums)!=1536:
        rgb.master.destroy()
        break
    rgb_arr = vis.update_rgb_array(vocals=voice,bass=bass,drums=drums,other=other)
    rgb.colorSquares(rgb_arr)
    rgb.update()
    if pygame_paused:
        start_time += time.time()-timer

sys.exit(0)
