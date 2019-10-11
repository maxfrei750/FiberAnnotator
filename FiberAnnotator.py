import tkinter as tk
from customized_classes import CustomTkCanvas
from PIL import ImageTk, Image
from spline import Spline
import os
from glob import glob


class FiberAnnotator:
    def __init__(self, root, image_paths):
        # Root
        self.root = root

        self.root.bind("<Up>", self.arrow_key)
        self.root.bind("<Down>", self.arrow_key)
        self.root.bind("<Left>", self.arrow_key)
        self.root.bind("<Right>", self.arrow_key)

        self.root.bind("<Return>", self.enter_key)
        self.root.bind("<space>", self.space_key)

        self.root.bind("<MouseWheel>", self.mouse_wheel_scroll)
        self.root.bind("<Button-4>", self.mouse_wheel_scroll)
        self.root.bind("<Button-5>", self.mouse_wheel_scroll)

        # Canvas
        self.canvas = CustomTkCanvas(root)
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
        self.splines = list()
        self.point_size = 2
        self.default_spline_width = 1
        self.image = None
        self.image_handle = None
        self.active_image_path = None
        self.image_paths = image_paths
        self.output_folder = None

        self.load_next_image()

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
            self.active_spline.width -= 1
        if event.num == 4 or event.delta == 120:
            self.active_spline.width += 1

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
        self.save_splines()
        self.delete_all_splines()
        self.delete_all_points()
        self.load_next_image()

    def space_key(self, event=None):
        self.delete_all_points()

    # Actions ----------------------------------------------------------------------------------------------------------
    def load_next_image(self):
        self.load_image(self.image_paths.pop(1))

    def save_splines(self):
        file_name_base = os.path.splitext(os.path.basename(self.active_image_path))[0]

        for spline_id, spline in enumerate(self.splines):
            spline.save(self.image_size, file_name_base, self.output_folder, spline_id)

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

    def delete_all_points(self):
        while self.point_handles:
            self.canvas.delete(self.point_handles.pop())

    def delete_all_splines(self):
        while self.splines:
            self.canvas.delete(self.splines.pop().handle)

    def place_point(self, x, y, color="red"):
        if not self.point_handles:
            self.create_new_spline()

        if self.point_handles:
            self.canvas.itemconfig(self.active_point_handle, fill="lime")

        point_handle = self.canvas.create_circle(x, y, self.point_size, fill=color, outline="", activefill="yellow")
        # TODO: Implement point selection.
        self.point_handles.append(point_handle)

        self.update_active_spline()

    def create_new_spline(self):
        if self.active_spline is None:
            width = self.default_spline_width
        else:
            width = self.active_spline.width

        self.splines.append(Spline(width=width))

    def update_active_spline(self):
        coordinates = list()

        if self.active_spline is None:
            width = self.default_spline_width
        else:
            width = self.active_spline.width

        n_point_handles = len(self.point_handles)

        if n_point_handles == 1:
            self.canvas.delete(self.active_spline.handle)

        if n_point_handles >= 2:
            self.delete_active_spline()
            for handle in self.point_handles:
                x1, y1, x2, y2 = self.canvas.bbox(handle)
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2

                coordinates.append([x, y])

            new_spline = Spline(coordinates, width=width)
            new_spline.handle = self.canvas.create_spline(coordinates, width=width, stipple="gray50")
            self.splines.append(new_spline)

    def delete_active_spline(self):
        if self.active_spline is not None:
            self.canvas.delete(self.splines.pop().handle)

    def load_image(self, image_path):
        self.output_folder = os.path.dirname(image_path)
        self.active_image_path = image_path
        self.image = ImageTk.PhotoImage(Image.open(image_path))

        w, h = self.image.width(), self.image.height()
        self.canvas.configure(width=w, height=h)

        if self.image_handle is not None:
            self.canvas.delete(self.image_handle)

        self.image_handle = self.canvas.create_image(w, h, image=self.image, anchor="se")

    # Properties -------------------------------------------------------------------------------------------------------
    @property
    def active_point_handle(self):
        if self.point_handles:
            return self.point_handles[-1]
        else:
            return None

    @property
    def active_spline(self):
        if self.splines:
            return self.splines[-1]
        else:
            return None

    @property
    def image_size(self):
        if self.image is None:
            return None
        else:
            return self.image.width(), self.image.height()


if __name__ == "__main__":
    root = tk.Tk()

    image_glob = os.path.join("test_images", "*.tif")
    image_paths = glob(image_glob)

    fiber_annotator = FiberAnnotator(root, image_paths)
    root.mainloop()
