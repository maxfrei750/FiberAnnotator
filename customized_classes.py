import tkinter as tk
import utilities


class CustomTkCanvas(tk.Canvas):
    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_spline(self, coordinates, **kwargs):
        coordinates = utilities.spline_interpolation(coordinates)
        return self.create_line(coordinates, **kwargs)
