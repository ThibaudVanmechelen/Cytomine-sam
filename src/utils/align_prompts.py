"""Module to align the prompts in the new referential."""

import numpy as np


def align_box_prompt(box: np.ndarray, x_tl: int, y_tl: int, img_height: int):
    """
    Function to align the box prompt with the extracted window (the coordinates of the box prompt
    must be relative to the window and not to the WSI, this function performs this transformation).

    Args:
        (box: np.ndarray): the box prompt with format: np.array([x_min, y_min, x_max, y_max]).
        (x_tl: int): the offset along the x-axis.
        (y_tl: int): the offset along the y-axis.
        (img_height): the height of the image.

    Returns:
        (np.ndarray): Returns the transformed box prompt.
    """
    x_min, y_min, x_max, y_max = box # bottom left referential

    y_min_flipped = img_height - y_max
    y_max_flipped = img_height - y_min

    new_x_min = x_min - x_tl
    new_x_max = x_max - x_tl
    new_y_min = y_min_flipped - y_tl
    new_y_max = y_max_flipped - y_tl

    return np.array([new_x_min, new_y_min, new_x_max, new_y_max])


def align_point_prompt(points: np.ndarray, x_tl: int, y_tl: int, img_height: int):
    """
    Function to align the point prompts with the extracted window (the coordinates of
    the point promptsmust be relative to the window and not to the WSI, this function
    performs this transformation).

    Args:
        (points: np.ndarray): the point prompts.
        (x_tl: int): the offset along the x-axis.
        (y_tl: int): the offset along the y-axis.
        (img_height): the height of the image.

    Returns:
        (np.ndarray): Returns the transformed point prompts.
    """
    for p in points: # p[0] = x, p[1] = y (bottom-left referential)
        p[1] = img_height - p[1]

        p[0] -= x_tl
        p[1] -= y_tl

    return points
