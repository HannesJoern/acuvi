import tkinter as tk


class control_window:

    def __init__(self) -> None:
        self.master = tk.Tk()
        self.master.geometry('200x50')
        self.w = tk.Button ( self.master, text = "Pause", command= self.pause,width=45,height=45)
        self.w.pack(side='left')
        self.ispaused = False

    def pause(self):
        if self.ispaused:
            self.ispaused = False
            return
        self.ispaused = True

    








