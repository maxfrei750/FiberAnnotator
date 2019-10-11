import numpy as np
from scipy import interpolate


def spline_interpolation(coordinates):
    if not coordinates or coordinates is None:
        return None

    n_coordinates = len(coordinates)

    if n_coordinates >= 4:
        coordinates = np.array(coordinates)

        x = coordinates[:, 0]
        y = coordinates[:, 1]

        tck, _ = interpolate.splprep([x, y], s=0)
        x_new, y_new = interpolate.splev(np.linspace(0, 1, n_coordinates * 12), tck, der=0)

        return np.stack((x_new, y_new), axis=-1).tolist()
    else:
        return coordinates
