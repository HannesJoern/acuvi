import math
import time
import tkinter as tk
import matplotlib.pyplot as plt
import scipy.fftpack
import numpy as np

class RGB_display:
    h = 0.8
    equ_frequqencystep=[218.75,437.5,875,1750,3500,7000]
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
        for i in range(11):
            if i<int((intensity/100)*11):
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
        """""""""
        combined = []
        for i in range(int(len(soundData) / 2)):
            combined.append(int((soundData[i * 2] + soundData[(i * 2) + 1]) / 2))
        yf = scipy.fftpack.rfft(combined)
        # xf = scipy.fftpack.rfftfreq(1536,1/48000)
        step = 1 / (len(soundData) / 48000)

        arr = yf[:24]
        sorted = np.sort(arr)

        l1 = np.where(arr == sorted[0])[0][0]
        l2 = np.where(arr == sorted[1])[0][0]
        l3 = np.where(arr == sorted[2])[0][0]

        index = int((l1+l2+l3)/3)-16
        """""""""
        zeros = 0
        freq = 0
        for i in range(len(soundData)-1):
            if (soundData[i] < 0 and soundData[i+1] > 0) or (soundData[i] > 0 and soundData[i+1] < 0):
                zeros += 1


        freq = zeros * int(48000/len(soundData))

        print(freq)
        step = 30
        index = int(math.pow(1.5,freq/step))
        for i in range(self.x_squares):
            if i != index:
                self.colorSquare(self.y_squares - 3, i, 255, 255, 255)
            else:
                self.colorSquare(self.y_squares - 3, index, 40, 204, 204)
        """""""""
        if yf[index]>3500 and index < self.x_squares:
            for i in range(self.x_squares):
                if i!=index:
                    self.colorSquare(self.y_squares - 3, i, 255, 255, 255)
                else:
                    self.colorSquare(self.y_squares-3,index,40,204,204)
        """""""""
        #print(yf[np.argmax(yf)])










