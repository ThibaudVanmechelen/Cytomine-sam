"""Module to test the align_prompts.py file"""

import numpy as np
from src.utils.align_prompts import align_box_prompt, align_point_prompt


def test_align_box_prompt():
    """Test function"""
    box = np.array([10, 20, 30, 40])
    x_tl, y_tl = 5, 10
    img_height = 100

    result = align_box_prompt(box, x_tl, y_tl, img_height)
    expected = np.array([5, 50, 25, 70])

    np.testing.assert_array_equal(result, expected)


def test_align_point_prompt():
    """Test function"""
    points = np.array([[10, 20], [30, 40]])
    x_tl, y_tl = 5, 10
    img_height = 100

    expected = np.array([[5, 70], [25, 50]])
    result = align_point_prompt(points.copy(), x_tl, y_tl, img_height)

    np.testing.assert_array_equal(result, expected)
