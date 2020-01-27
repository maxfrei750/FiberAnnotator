import os
import random
import tkinter as tk
import warnings
from glob import glob
from tkinter import messagebox

from customized_classes import CustomTkCanvas
from PIL import Image, ImageTk
from spline import Spline


class FiberAnnotator:
    def __init__(self, root, image_paths):
        # Root
        self.root = root

        self.root.bind("<Up>", self.arrow_key)
        self.root.bind("w", self.arrow_key)
        self.root.bind("<Down>", self.arrow_key)
        self.root.bind("s", self.arrow_key)
        self.root.bind("<Left>", self.arrow_key)
        self.root.bind("a", self.arrow_key)
        self.root.bind("<Right>", self.arrow_key)
        self.root.bind("d", self.arrow_key)

        self.root.bind("<Return>", self.enter_key)
        self.root.bind("e", self.enter_key)
        self.root.bind("<space>", self.space_key)
        self.root.bind("<Delete>", self.delete_key)

        self.root.bind("<MouseWheel>", self.mouse_wheel_scroll)
        self.root.bind("<Button-4>", self.mouse_wheel_scroll)
        self.root.bind("<Button-5>", self.mouse_wheel_scroll)

        # Canvas
        self.canvas = CustomTkCanvas(root)
        self.canvas.pack()
        self.canvas.tag_bind("image", "<1>", self.image_onclick)
        self.canvas.tag_bind("point", "<1>", self.point_onclick)

        self.canvas.bind("<ButtonPress-3>", self.right_mouse_button_down)
        self.canvas.bind("<ButtonRelease-3>", self.right_mouse_button_up)

        # Visible properties
        self.is_left_mouse_button_down = False
        self.is_right_mouse_button_down = False
        self.point_handles = list()
        self.active_point_handle = None
        self.splines = list()
        self.point_size = 4
        self.default_spline_width = 1
        self.image = None
        self.image_handle = None
        self.active_image_path = None
        self.image_paths = image_paths
        self.output_folder = None

        self.load_next_image()

    # Mouse ------------------------------------------------------------------------------------------------------------
    def right_mouse_button_down(self, event=None):
        self.is_right_mouse_button_down = True

    def right_mouse_button_up(self, event=None):
        self.is_right_mouse_button_down = False
        self.delete_last_point()

    def mouse_wheel_scroll(self, event=None):
        if self.active_spline is not None:
            if event.num == 5 or event.delta == -120:
                self.active_spline.width -= 1
            if event.num == 4 or event.delta == 120:
                self.active_spline.width += 1

            self.update_active_spline()

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

    def delete_key(self, event=None):
        self.delete_active_spline()
        self.delete_all_points()

    # Actions ----------------------------------------------------------------------------------------------------------
    def point_onclick(self, event=None):
        if self.active_point_handle is not None:
            self.canvas.itemconfig(self.active_point_handle, fill="lime")

        # Search for the caller.
        x = event.x
        y = event.y

        found_type = None

        while found_type != "oval":
            x += random.randint(-1, 1)
            y += random.randint(-1, 1)

            found_handle = self.canvas.find_closest(x, y)
            found_type = self.canvas.type(found_handle)

        self.active_point_handle = found_handle
        self.canvas.itemconfig(self.active_point_handle, fill="red")

    def image_onclick(self, event=None):
        self.place_point(event.x, event.y)

    def load_next_image(self):
        if self.image_paths:
            self.load_image(self.image_paths.pop(0))
        else:
            messagebox.showinfo(
                "Last image.", "Congratulations! You annotated all images."
            )
            self.quit()

    def quit(self):
        self.root.destroy()

    def save_splines(self):
        file_name_base = os.path.splitext(
            os.path.basename(self.active_image_path)
        )[0]

        for spline_id, spline in enumerate(self.splines):
            spline.save(
                self.image_size, file_name_base, self.output_folder, spline_id
            )

    def move_active_point(self, direction):
        direction = direction.lower()

        if self.active_point_handle is not None:

            _, _, x, y = self.canvas.coords(self.active_point_handle)

            dx, dy = 0, 0

            if direction == "up" or direction == "w":
                dy = -1
            elif direction == "down" or direction == "s":
                dy = 1
            elif direction == "left" or direction == "a":
                dx = -1
            elif direction == "right" or direction == "d":
                dx = 1

            x_new = x + dx
            y_new = y + dy

            w, h = self.image.width(), self.image.height()

            if 4 <= x_new <= w:
                self.canvas.move(self.active_point_handle, dx, 0)

            if 4 <= y_new <= h:
                self.canvas.move(self.active_point_handle, 0, dy)

            self.update_active_spline()

    def delete_last_point(self):
        if self.last_point_handle is not None:
            if self.active_point_handle is not None:
                self.canvas.itemconfig(self.active_point_handle, fill="lime")
            self.canvas.delete(self.point_handles.pop())
            if self.last_point_handle is not None:
                self.canvas.itemconfig(self.last_point_handle, fill="red")

            self.active_point_handle = self.last_point_handle

            if self.last_point_handle is None:
                self.delete_active_spline()

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

        self.canvas.dtag("active", "active")
        point_handle = self.canvas.create_circle(
            x,
            y,
            self.point_size,
            fill=color,
            outline="",
            activefill="yellow",
            tags=("point",),
        )
        self.point_handles.append(point_handle)
        self.active_point_handle = self.point_handles[-1]
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
            new_spline.handle = self.canvas.create_spline(
                coordinates, width=width, stipple="gray50"
            )
            self.canvas.tag_lower(new_spline.handle)
            self.canvas.tag_lower(self.image_handle)
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

        self.image_handle = self.canvas.create_image(
            w, h, image=self.image, anchor="se", tags=("image",)
        )

    # Properties -------------------------------------------------------------------------------------------------------
    @property
    def last_point_handle(self):
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

    image_glob = os.path.join(
        "d:/",
        "sciebo",
        "Dissertation",
        "Referenzdaten",
        "IUTA",
        "easy_images",
        "not done yet",
        "overlapping",
        "*.png",
    )

    image_paths = glob(image_glob)

    image_paths.sort()

    # Filter mask images.
    image_paths = [
        image_path
        for image_path in image_paths
        if "mask" not in os.path.basename(image_path)
    ]

    # Skip files that were already evaluated.
    image_paths_to_process = list()
    for image_path in image_paths:
        base_name = os.path.splitext(image_path)[0]

        # Look for auxiliary files.
        auxiliary_files_data = glob(base_name + "_spline*.csv")

        num_auxiliary_files = len(auxiliary_files_data)

        if num_auxiliary_files == 0:
            image_paths_to_process.append(image_path)
        else:
            warnings.warn(
                "Skipped file because it already has auxiliary files: "
                + image_path,
                UserWarning,
            )

    fiber_annotator = FiberAnnotator(root, image_paths_to_process)
    root.mainloop()
