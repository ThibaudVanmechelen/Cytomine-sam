import numpy as np
from typing import List
from api.models.model import GeoJsonPoint
from utils.format_prompt import format_point_prompt


def align_box_prompt(box: np.ndarray, x_tl: int, y_tl: int, img_height: int):
    x_min, y_min, x_max, y_max = box # bottom left referential

    y_min_flipped = img_height - y_max
    y_max_flipped = img_height - y_min

    new_x_min = x_min - x_tl
    new_x_max = x_max - x_tl
    new_y_min = y_min_flipped - y_tl
    new_y_max = y_max_flipped - y_tl

    return np.array([new_x_min, new_y_min, new_x_max, new_y_max])


def align_point_prompt(points: List[GeoJsonPoint], x_tl: int, y_tl: int, img_height: int):
    point_coords, point_labels = format_point_prompt(points)
    
    for p in point_coords: # p[0] = x, p[1] = y (bottom-left referential)
        p[1] = img_height - p[1]

        p[0] -= x_tl
        p[1] -= y_tl

    return point_coords, point_labels
