import pytest
import numpy as np

from src.utils.convert_coordinates import *

@pytest.mark.parametrize("coords, image_height, expected", [
    ([[0, 0], [100, 100]], 200, [[0, 200], [100, 100]]),
    ([[50, 50]], 100, [[50, 50]]),
    ([[10, 90], [20, 80]], 100, [[10, 10], [20, 20]]),
    ([], 100, []),
])

def test_convert_to_opencv_coords(coords, image_height, expected):
    result = convert_to_opencv_coords(coords, image_height)
    np.testing.assert_array_almost_equal(result, np.array(expected, dtype = np.float32))

@pytest.mark.parametrize("box, image_height, expected", [
    ([10, 20, 30, 40], 100, [10, 60, 30, 80]),
    ([0, 0, 0, 0], 100, [0, 100, 0, 100]),
    ([5, 5, 15, 15], 20, [5, 5, 15, 15]),
    ([0, 90, 10, 100], 100, [0, 0, 10, 10]),
])

def test_convert_box_coordinates(box, image_height, expected):
    result = convert_box_coordinates(np.array(box, dtype = np.float32), image_height)
    np.testing.assert_array_almost_equal(result, np.array(expected, dtype = np.float32))

@pytest.mark.parametrize("points, image_height, expected", [
    ([[10, 10]], 20, [[10, 10]]),
    ([[0, 0], [50, 50]], 100, [[0, 100], [50, 50]]),
    ([[5, 95], [10, 90]], 100, [[5, 5], [10, 10]]),
    ([], 50, []),
])

def test_convert_point_coordinates(points, image_height, expected):
    result = convert_point_coordinates(np.array(points, dtype = np.float32), image_height)
    np.testing.assert_array_almost_equal(result, np.array(expected, dtype = np.float32))