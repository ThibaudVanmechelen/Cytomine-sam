import numpy as np
from typing import Union, List


def convert_to_opencv_coords(coords: Union[np.ndarray, List[List[float]]], image_height: int):
    coords = np.array(coords, dtype = np.float32)
    coords[:, 1] = image_height - coords[:, 1]

    return coords


def convert_box_coordinates(box: np.ndarray, image_height: int):
    x_min, y_min, x_max, y_max = box

    y_min_new = image_height - y_max
    y_max_new = image_height - y_min

    return np.array([x_min, y_min_new, x_max, y_max_new], dtype = np.float32)


def convert_point_coordinates(points: np.ndarray, image_height: int):
    return convert_to_opencv_coords(points, image_height)