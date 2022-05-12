import math
import time
import tkinter as tk
import matplotlib.pyplot as plt
import scipy.fftpack
import aubio
import numpy as np

class RGB_display:
    h = 0.8
    equ_frequqencystep=[218.75,437.5,875,1750,3500,7000]
    freq = [55 * pow(1.0594,i) for i in range(20)]
    notes = ['B1','C2','D2','E2','F2','G2','A2','B2','C3','D3','E3','F3','G3','A3','B3','C4']

    def __init__(self,x_squares:int,y_squares:int):
        self.x_squares = x_squares
        self.y_squares = y_squares
        self.master = tk.Tk()
        self.squares_coordinates = [[]]
        self.square_side = int((self.master.winfo_screenwidth() * self.h)/x_squares)
        self.width = int(self.master.winfo_screenwidth() * self.h)
        self.height = int(self.master.winfo_screenheight() * self.h)

        if x_squares > y_squares:
            height = int(self.height * (self.y_squares / self.x_squares))
        else:
            width = int(self.width * (self.x_squares / self.y_squares))

        self.master.geometry(str(self.width) + 'x' + str(self.height))
        self.canvas = tk.Canvas(master=self.master, height=self.height, width=self.width, bd=0)
        self.prev_bass_index = [0,0,0,0,0,0]
        self.stable_index = 0



    def createRgbDisplay(self):
        for y in range(self.y_squares):
            self.squares_coordinates.append([])
            for x in range(self.x_squares):
                corner_x = x*self.square_side
                corner_y = y*self.square_side
                self.squares_coordinates[y].append(self.canvas.create_rectangle(corner_x, corner_y, corner_x + self.square_side, corner_y + self.square_side, fill="white",outline='black'))
        self.canvas.pack()

    def colorSquare(self,line_nr:int,column_nr:int,red:int,green:int,blue:int):
        colorval = "#%02x%02x%02x" % (red, green, blue)
        self.canvas.itemconfig(self.squares_coordinates[line_nr][column_nr], fill=colorval)

    def clearSquares(self):
        for x in self.squares_coordinates:
            for y in x:
                self.canvas.itemconfig(y,fill='white')

    def update(self):
        self.master.update()

    def fftDisplay(self, sampleRate: int, soundData: [], sampleLength: int):

        combined = []
        for i in range(int(len(soundData) / 2)):
            combined.append(int((soundData[i * 2] + soundData[(i * 2) + 1]) / 2))
        yf = scipy.fftpack.rfft(combined)
        #xf = scipy.fftpack.rfftfreq(1536,1/48000)
        step = 1/(sampleLength/sampleRate)
        #plt.plot(xf,abs(yf))
        #plt.show()


        value = 0
        pos = 0
        values = []
        for i in range(len(yf)):
            if(abs(yf[i]>value)):
                value = abs(yf[i])
            if step*i == self.equ_frequqencystep[pos]:
                values.append(int(value))
                value = 0
                pos += 1
            if pos == len(self.equ_frequqencystep):
                break

        for i in range(6):
            for h in range(int((values[i]/2000000)*12)):
                if h<=12:
                    self.colorSquare(12-h,i*3,0,204,204)
                    self.colorSquare(12-h, (i * 3)+1, 0, 204, 204)
                    self.colorSquare(12-h, (i * 3)+2, 0, 204, 204)
        self.update()

    def drums(self,soundData: []):
        intensity = max(soundData)
        for i in range(12):
            r = int((intensity/100)*11)
            if r==0:
                r=1
            if i<r:
                self.colorSquare(self.y_squares - 1, 11 - i,int((254/11)*i),0,204)
                self.colorSquare(self.y_squares - 2, 11 - i,int((254/11)*i),0,204)
                self.colorSquare(self.y_squares - 1, 12 + i,int((254/11)*i),0,204)
                self.colorSquare(self.y_squares - 2, 12 + i,int((254/11)*i),0,204)
            else:
                self.colorSquare(self.y_squares - 1, 11 - i, 255, 255, 255)
                self.colorSquare(self.y_squares - 2, 11 - i, 255, 255, 255)
                self.colorSquare(self.y_squares - 1, 12 + i, 255, 255, 255)
                self.colorSquare(self.y_squares - 2, 12 + i, 255, 255, 255)


    def bass(self,soundData: []):
        data_max = max(soundData)
        intensity = int(round(math.log(data_max+0.1,3)))
        if intensity <2 or data_max<1:
            intensity = 0
        #print(str(max(soundData)) + " " + str(intensity))
        soundDataNew = np.array(soundData, dtype='float32')
        pitchdetector = aubio.pitch("yin",buf_size=1536,samplerate=48000,hop_size=1536)

        pitchdetector.set_tolerance(0.8)
        pitch = pitchdetector(soundDataNew)[0]


        ind = 0
        diff = 0xFFFFFFFF

        for i in range(len(RGB_display.freq)):
            difference = abs(pitch-RGB_display.freq[i])
            if difference < diff:
                diff = difference
                ind = i

        self.add_pitch(ind)
        if self.is_array_equal():
            index = ind
        else:
            index = self.stable_index
        self.stable_index = index
        #print(RGB_display.notes[index])

        for i in range(self.x_squares):
            if i != index:
                for u in range(4):
                    self.colorSquare(self.y_squares - 3-u, i, 255, 255, 255)
            else:
                for u in range(intensity):
                    if u < 4:
                        self.colorSquare(self.y_squares - 3-u, index, 40, 204, 204)

    def is_array_equal(self):
        for i in self.prev_bass_index:
            if self.prev_bass_index[0] != i:
                return False
        return True

    def add_pitch(self,p):
        for i in range(5):
            self.prev_bass_index[i+1] = self.prev_bass_index[i]
        self.prev_bass_index[0] = p








