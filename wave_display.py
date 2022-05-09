import tkinter
from tkinter import *
from tkinter import ttk
from random import randint
from typing import List

import numpy as np
from scipy.signal import savgol_filter


def createWindow():
    master = Tk()
    master.geometry("1536x300")
    canvas = Canvas(master=master, height=300, width=1536, bd=0)
    canvas.pack()
    return master, canvas




def graph(arr,canvas:tkinter.Canvas):
    lista = []

    for u in range(len(arr)*2):
        if u % 2 == 1:
            lista.append((arr[int(u/2)] - 120) % 255)
        else:
            lista.append(int(u/2))
    
    canvas.create_line(lista)



def clear(canvas):
    canvas.delete("all")


def update(master:tkinter.Tk):
    master.update()



