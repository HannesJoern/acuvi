import math
import time
import tkinter as tk
import matplotlib.pyplot as plt
import scipy.fftpack
import numpy as np

class RGB_display:
    h = 0.8 #size of window given in percentage relative to the screen size
    equ_frequqencystep=[218.75,437.5,875,1750,3500,7000] # range of frequency bands in fft-visualiation
    
    #initialiser, x_squares is the number of squares width and y_squares in height
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


    #creates and opens the window
    def createRgbDisplay(self):
        for y in range(self.y_squares):
            self.squares_coordinates.append([])
            for x in range(self.x_squares):
                corner_x = x*self.square_side
                corner_y = y*self.square_side
                self.squares_coordinates[y].append(self.canvas.create_rectangle(corner_x, corner_y, corner_x + self.square_side, corner_y + self.square_side, fill="white",outline='black'))
        self.canvas.pack()
    
    # colors the square with coordinates (line_re,column_nr), the most top left square is on line_nr:0 and column_nr:0
    def colorSquare(self,line_nr:int,column_nr:int,red:int,green:int,blue:int):
        colorval = "#%02x%02x%02x" % (red, green, blue)
        self.canvas.itemconfig(self.squares_coordinates[line_nr][column_nr], fill=colorval)
    
    #sets color of all squares to white
    def clearSquares(self):
        for x in self.squares_coordinates:
            for y in x:
                self.canvas.itemconfig(y,fill='white')
    
    #updates the window and shows all changes
    def update(self):
        self.master.update()
    
    #displays the fft transformation in bands of different frequency ranges specified in equ_frequencystep 
    def fftDisplay(self, sampleRate: int, soundData: [], sampleLength: int):

        combined = []
        for i in range(int(len(soundData) / 2)):
            combined.append(int((soundData[i * 2] + soundData[(i * 2) + 1]) / 2))
        yf = scipy.fftpack.rfft(combined)

        step = 1/(sampleLength/sampleRate)
        


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
    
    #visualizes the drums, input data is spleeter drums result, anly length works
    #this only works with a window length of 24 squares
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

    
    #this shit is just plain broken, use if you want to summon satan
    def bass(self,soundData: []):
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
        if yf[index]>3500 and index < self.x_squares:
            for i in range(self.x_squares):
                if i!=index:
                    self.colorSquare(self.y_squares - 3, i, 255, 255, 255)
                else:
                    self.colorSquare(self.y_squares-3,index,40,204,204)

        #print(yf[np.argmax(yf)])










