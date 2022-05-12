
import time
from threading import Thread

import vlc

import RGB_display
import wav_4_stems
import wave_display


#creates all the windows for visualisation, i use vlc for the playback of the files, you can use whatever library or format u like, for this to work
#you have to have 4 files int the same directory as this file, music.mp3, vocals.wav,bass.wav,drums.wav and other.wav and you have to have vlc installed
#note if the version of your installed vlc instance (32bit/64bit) has to correspond with your operating system version
wav_data = wav_4_stems

masterV, canvasV = wave_display.createWindow()
masterB, canvasB = wave_display.createWindow()
masterD, canvasD = wave_display.createWindow()
masterO, canvasO = wave_display.createWindow()
masterV.title("Voice")
masterB.title("Bass")
masterD.title("Drums")
masterO.title("Other")
rgb = RGB_display.RGB_display(24,12)
rgb.createRgbDisplay()
position = 0
secondsPerFrame = 1/(wav_data.samplerate/1536*4)
print("done 1 seconds before start")
time.sleep(1)
p = vlc.MediaPlayer("music.mp3")
start_time = time.time()
p.play()

#loop for visualistaion
while True:

    timer = time.time()
    data, pos = wav_data.getFrames(frames=1536*4, position=int((timer-start_time)*wav_data.samplerate))
    voice = data[0]
    bass = data[1]
    drums = data[2]
    other = data[3]

    #print(len(bass))
    #print(voice)

    wave_display.clear(canvasV)
    wave_display.clear(canvasB)
    wave_display.clear(canvasD)
    wave_display.clear(canvasO)
    #rgb.clearSquares()

    Thread(target=wave_display.graph(voice, canvasV)).start()
    Thread(target=wave_display.graph(bass, canvasB)).start()
    Thread(target=wave_display.graph(drums, canvasD)).start()
    Thread(target=wave_display.graph(other, canvasO)).start()
    rgb.drums(drums)
    rgb.bass(bass)

    rgb.update()
    wave_display.update(masterV)
    wave_display.update(masterB)
    wave_display.update(masterD)
    wave_display.update(masterO)
    #print((time.time()-timer)*1000.0)
    if (0.05-(time.time()-timer))>0.01:
        time.sleep(0.05-(time.time()-timer))
