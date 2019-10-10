import tkinter as tk
from custom_canvas import CustomCanvas
from PIL import ImageTk, Image, ImageGrab


class FiberAnnotator:
    def __init__(self, root):
        # Root
        self.root = root

        self.root.bind("<Up>", self.arrow_key)
        self.root.bind("<Down>", self.arrow_key)
        self.root.bind("<Left>", self.arrow_key)
        self.root.bind("<Right>", self.arrow_key)

        self.root.bind("<Return>", self.enter_key)

        self.root.bind("<MouseWheel>", self.mouse_wheel_scroll)
        self.root.bind("<Button-4>", self.mouse_wheel_scroll)
        self.root.bind("<Button-5>", self.mouse_wheel_scroll)

        # Canvas
        self.canvas = CustomCanvas(root)
        self.canvas.pack()

        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<ButtonPress-1>", self.left_mouse_button_down)
        self.canvas.bind("<ButtonRelease-1>", self.left_mouse_button_up)
        self.canvas.bind("<ButtonPress-3>", self.right_mouse_button_down)
        self.canvas.bind("<ButtonRelease-3>", self.right_mouse_button_up)

        # Visible properties
        self.is_left_mouse_button_down = False
        self.is_right_mouse_button_down = False
        self.point_handles = list()
        self.spline_handles = list()
        self.point_size = 2
        self.image = None
        self.image_handle = None
        self.image_path = None

        # Hidden properties
        self.__active_spline_width = 1

        # Load image
        # TODO: Write routine to glob through images.
        self.load_image("testimage.tif")

    # Mouse ------------------------------------------------------------------------------------------------------------
    def left_mouse_button_down(self, event=None):
        # TODO: implement drag and drop of points
        # self.is_left_mouse_button_down = True
        # self.delete_active_point()
        pass

    def left_mouse_button_up(self, event=None):
        self.is_left_mouse_button_down = False
        self.place_point(event.x, event.y)

    def right_mouse_button_down(self, event=None):
        self.is_right_mouse_button_down = True

    def right_mouse_button_up(self, event=None):
        self.is_right_mouse_button_down = False
        self.delete_active_point()

    def mouse_wheel_scroll(self, event=None):
        if event.num == 5 or event.delta == -120:
            self.active_spline_width -= 1
        if event.num == 4 or event.delta == 120:
            self.active_spline_width += 1

        self.update_active_spline()

    def motion(self, event=None):
        # TODO: Implement drag and drop for points.
        # if self.is_left_mouse_button_down:
        #     self.delete_active_point()
        #     self.place_point(event.x, event.y, color="yellow")
        pass

    # Keys -------------------------------------------------------------------------------------------------------------
    def arrow_key(self, event=None):
        self.move_active_point(event.keysym)

    def enter_key(self, event=None):
        self.save_image("test.png")

    # Actions ----------------------------------------------------------------------------------------------------------
    def move_active_point(self, direction):
        direction = direction.lower()

        if self.active_point_handle is not None:

            _, _, x, y = self.canvas.coords(self.active_point_handle)

            dx, dy = 0, 0

            if direction == "up":
                dy = -1
            elif direction == "down":
                dy = 1
            elif direction == "left":
                dx = -1
            elif direction == "right":
                dx = 1

            x_new = x + dx
            y_new = y + dy

            w, h = self.image.width(), self.image.height()

            if 4 <= x_new <= w:
                self.canvas.move(self.active_point_handle, dx, 0)

            if 4 <= y_new <= h:
                self.canvas.move(self.active_point_handle, 0, dy)

            self.update_active_spline()

    def delete_active_point(self):
        if self.active_point_handle is not None:
            self.canvas.delete(self.point_handles.pop())
            if self.active_point_handle is not None:
                self.canvas.itemconfig(self.active_point_handle, fill="red")

            self.update_active_spline()

    def place_point(self, x, y, color="red"):
        if self.point_handles:
            self.canvas.itemconfig(self.active_point_handle, fill="lime")

        point_handle = self.canvas.create_circle(x, y, self.point_size, fill=color, outline="", activefill="yellow")
        # TODO: Implement point selection.
        self.point_handles.append(point_handle)

        self.update_active_spline()

    def change_active_spline_width(self, amount):
        if self.active_spline_handle is not None:
            current_width = float(self.canvas.itemcget(self.active_spline_handle, "width"))
            new_width = current_width + amount

            if new_width < 1:
                new_width = 1

            self.canvas.itemconfig(self.active_spline_handle, width=new_width)

    def update_active_spline(self):
        self.delete_active_spline()

        coordinates = list()

        if len(self.point_handles) >= 2:
            for handle in self.point_handles:
                x1, y1, x2, y2 = self.canvas.bbox(handle)
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2

                coordinates.append((x, y))

            self.spline_handles.append(self.canvas.create_spline(coordinates, width=self.active_spline_width, stipple="gray50"))

    def delete_active_spline(self):
        if self.active_spline_handle is not None:
            self.canvas.delete(self.spline_handles.pop())

    def load_image(self, image_path):
        self.image_path = image_path
        self.image = ImageTk.PhotoImage(Image.open(image_path))

        w, h = self.image.width(), self.image.height()
        self.canvas.configure(width=w, height=h)
        self.image_handle = self.canvas.create_image(w, h, image=self.image, anchor="se")

    def save_image(self, file_name):
        x = self.root.winfo_rootx() + self.canvas.winfo_x()
        y = self.root.winfo_rooty() + self.canvas.winfo_y()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(file_name)

    # Properties -------------------------------------------------------------------------------------------------------
    @property
    def active_point_handle(self):
        if self.point_handles:
            return self.point_handles[-1]
        else:
            return None

    @property
    def active_spline_handle(self):
        if self.spline_handles:
            return self.spline_handles[-1]
        else:
            return None

    @property
    def active_spline_width(self):
        return self.__active_spline_width

    @active_spline_width.setter
    def active_spline_width(self, active_spline_width):
        if active_spline_width < 1:
            self.__active_spline_width = 1
        else:
            self.__active_spline_width = active_spline_width


if __name__ == "__main__":
    root = tk.Tk()
    fiber_annotator = FiberAnnotator(root)
    root.mainloop()
