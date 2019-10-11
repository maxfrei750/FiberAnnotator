import utilities
from PIL import Image, ImageDraw
import math
import os

class Spline:
    def __init__(self, points=None, width=1, handle=None):
        self._width = None
        self.width = width
        self.handle = handle
        self.points_raw = points

    def get_mask(self, image_size):
        points = self.points_interpolated

        points = [tuple(x) for x in points]

        mask = Image.new("L", image_size, 0)
        ImageDraw.Draw(mask).line(points, fill=255, width=self.width)

        # Draw ellipses at the line joins to cover up gaps.
        r = math.floor(self.width / 2) - 1.5

        for point in points[1:-1]:
            x, y = point
            x0 = x - r
            y0 = y - r
            x1 = x + r
            y1 = y + r

            ImageDraw.Draw(mask).ellipse([x0, y0, x1, y1], fill=255)

        return mask

    def save(self, image_size, file_name_base, output_folder, spline_id):
        mask = self.get_mask(image_size)
        mask_file_name = file_name_base + "_mask{:06d}.png".format(spline_id)
        mask_file_path = os.path.join(output_folder, mask_file_name)
        mask.save(mask_file_path)



    @property
    def points_interpolated(self):
        return utilities.spline_interpolation(self.points_raw)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if value < 1:
            self._width = 1
        else:
            self._width = value
