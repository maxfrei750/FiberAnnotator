import numpy as np
from scipy import interpolate


def spline_interpolation(coordinates):
    n_interpolation_steps = 8

    if not coordinates or coordinates is None:
        return None

    n_coordinates = len(coordinates)

    if n_coordinates >= 4:
        coordinates = np.array(coordinates).transpose()
        tck, _ = interpolate.splprep(coordinates, s=0)
        x_new, y_new = interpolate.splev(
            np.linspace(0, 1, n_coordinates * n_interpolation_steps),
            tck,
            der=0,
        )

        return np.stack((x_new, y_new), axis=-1).tolist()
    else:
        return coordinates
