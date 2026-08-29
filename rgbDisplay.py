"""A Tkinter-based grid of colored squares, used as a software stand-in for the physical
LED strip (see acuvi.py's `mode` setting). Handy for developing/testing without hardware.
"""

import tkinter as tk

from PIL import ImageColor


class RGB_display:
    """A resizable grid of colored squares rendered in a Tkinter window."""

    def __init__(self, x_squares: int, y_squares: int):
        self.x_squares = x_squares
        self.y_squares = y_squares
        self.master = tk.Tk()
        self.squares_coordinates = [[]]

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        self.square_side = int(screen_width / x_squares)
        self.width = screen_width
        self.height = screen_height

        self.master.geometry(f"{self.width}x{self.height}")
        self.canvas = tk.Canvas(master=self.master, height=self.height, width=self.width, bd=0)

    def createRgbDisplay(self):
        """Build the grid of rectangles and pack the canvas into the window."""
        for y in range(self.y_squares):
            self.squares_coordinates.append([])
            for x in range(self.x_squares):
                corner_x = x * self.square_side
                corner_y = y * self.square_side
                self.squares_coordinates[y].append(
                    self.canvas.create_rectangle(
                        corner_x, corner_y,
                        corner_x + self.square_side, corner_y + self.square_side,
                        fill="white", outline="black",
                    )
                )
        self.canvas.pack()

    def colorSquare(self, line_nr: int, column_nr: int, red: int, green: int, blue: int):
        """Set a single square's color by (row, column) index."""
        colorval = "#%02x%02x%02x" % (red, green, blue)
        self.canvas.itemconfig(self.squares_coordinates[line_nr][column_nr], fill=colorval)

    def colorSquares(self, vis_sample):
        """Set every square's color at once from a flat list of '#RRGGBB' strings."""
        i = 0
        for row in self.squares_coordinates:
            for square in row:
                self.canvas.itemconfig(square, fill=vis_sample[i])
                i += 1

    def clearSquares(self):
        """Reset every square to white."""
        for row in self.squares_coordinates:
            for square in row:
                self.canvas.itemconfig(square, fill="white")

    def update(self):
        """Redraw the Tkinter window. Must be called once per frame."""
        self.master.update()

    def getSquareColor(self, x_coord, y_coord):
        """Read back a square's current color as an (R, G, B) tuple."""
        color = self.canvas.itemcget(self.squares_coordinates[x_coord][y_coord], "fill")
        return ImageColor.getcolor(color, "RGB")
