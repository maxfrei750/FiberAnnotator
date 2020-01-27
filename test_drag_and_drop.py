import os
import string
import sys
import time
import tkinter as tk

# A Python example of drag and drop functionality within a single Tk widget.
# The trick is in the bindings and event handler functions.
# Tom Vrankar twv at ici.net

# empirical events between dropee and target, as determined from Tk 8.0
# down.
# leave.
# up, leave, enter.


class CanvasDnD(tk.Frame):
    def __init__(self, master):
        self.master = master
        self.loc = self.dragged = 0
        tk.Frame.__init__(self, master)
        canvas = tk.Canvas(
            self,
            width=256,
            height=256,
            relief=tk.RIDGE,
            background="white",
            borderwidth=1,
        )
        self.defaultcolor = canvas.itemcget(
            canvas.create_text(
                30, 25, font=("Helvetica", 14), text="Item 1", tags="DnD"
            ),
            "fill",
        )
        canvas.create_text(
            75, 75, font=("Helvetica", 14), text="Item 2", tags="DnD"
        )
        canvas.create_text(
            125, 125, font=("Helvetica", 14), text="Item 3", tags="DnD"
        )
        canvas.create_text(
            175, 175, font=("Helvetica", 14), text="Item 4", tags="DnD"
        )
        canvas.create_text(
            225, 225, font=("Helvetica", 14), text="Item 5", tags="DnD"
        )
        canvas.pack(expand=1, fill=tk.BOTH)
        canvas.tag_bind("DnD", "<ButtonPress-1>", self.down)
        canvas.tag_bind("DnD", "<ButtonRelease-1>", self.chkup)
        canvas.tag_bind("DnD", "<Enter>", self.enter)
        canvas.tag_bind("DnD", "<Leave>", self.leave)

    def down(self, event):
        print("Click on %s" % event.widget.itemcget(tk.CURRENT, "text"))
        self.loc = 1
        self.dragged = 0
        event.widget.bind("<Motion>", self.motion)

    def motion(self, event):
        root.config(cursor="exchange")
        cnv = event.widget
        cnv.itemconfigure(tk.CURRENT, fill="blue")
        x, y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        got = event.widget.coords(tk.CURRENT, x, y)

    def leave(self, event):
        self.loc = 0

    def enter(self, event):
        self.loc = 1
        if self.dragged == event.time:
            self.up(event)

    def chkup(self, event):
        event.widget.unbind("<Motion>")
        root.config(cursor="")
        self.target = event.widget.find_withtag(tk.CURRENT)
        event.widget.itemconfigure(tk.CURRENT, fill=self.defaultcolor)
        if self.loc:  # is button released in same widget as pressed?
            self.up(event)
        else:
            self.dragged = event.time

    def up(self, event):
        event.widget.unbind("<Motion>")
        if self.target == event.widget.find_withtag(tk.CURRENT):
            print("Select %s" % event.widget.itemcget(tk.CURRENT, "text"))

        else:
            event.widget.itemconfigure(tk.CURRENT, fill="blue")
            self.master.update()
            time.sleep(0.1)
            print(
                "%s Drag-N-Dropped onto %s"
                % (
                    event.widget.itemcget(self.target, "text"),
                    event.widget.itemcget(tk.CURRENT, "text"),
                )
            )
            event.widget.itemconfigure(tk.CURRENT, fill=self.defaultcolor)


root = tk.Tk()
root.title("Drag-N-Drop Demo")
CanvasDnD(root).pack()
root.mainloop()
