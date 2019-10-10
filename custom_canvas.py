import tkinter as tk


class CustomCanvas(tk.Canvas):
    def create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def create_spline(self, coords, **kwargs):
        return self.create_line(coords, smooth=1, splinesteps=12, **kwargs)
