from PIL import ImageColor
import tkinter as tk
from PIL import ImageColor

class RGB_display:

    h = 1
    #equ_frequqencystep=[218.75,437.5,875,1750,3500,7000]
    #freq = [55 * pow(1.0594,i) for i in range(20)]
    #notes = ['B1','C2','D2','E2','F2','G2','A2','B2','C3','D3','E3','F3','G3','A3','B3','C4']

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



    def colorSquares(self, vis_sample):
        i = 0
        for x in self.squares_coordinates:
            for y in x:
                self.canvas.itemconfig(y, fill=vis_sample[i])
                i += 1

    def getSquareColor(self,x_coord,y_coord):
        canvas = self.canvas
        color = self.canvas.itemcget(self.squares_coordinates[x_coord][y_coord], "fill")
        return ImageColor.getcolor(color,"RGB")

