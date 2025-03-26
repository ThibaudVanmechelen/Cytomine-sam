import pytest
import numpy as np

from src.api.models.model import *
from src.utils.format_prompt import *

@pytest.mark.parametrize("points_data, expected_coords, expected_labels", [
    ([GeoJsonPoint([1, 2], 0), GeoJsonPoint([3, 4], 1)], [[1, 2], [3, 4]], [0, 1]),
    ([GeoJsonPoint([0, 0], 5)], [[0, 0]], [5]),
    ([], None, None),
])

def test_format_point_prompt(points_data, expected_coords, expected_labels):
    coords, labels = format_point_prompt(points_data)

    if coords is None and labels is None:
        assert expected_coords is None and expected_labels is None

    else:
        np.testing.assert_array_equal(coords, np.array(expected_coords, dtype = np.float32))
        np.testing.assert_array_equal(labels, np.array(expected_labels, dtype = np.int32))

@pytest.mark.parametrize("polygon, expected", [
    (GeoJSONPolygon([[[1, 2], [3, 2], [3, 4], [1, 4], [1, 2]]]), [1, 2, 3, 4]),
    (GeoJSONPolygon([[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]]), [0, 0, 0, 0]),
    (GeoJSONPolygon([]), None),
    (GeoJSONPolygon([[[1, 2], [3, 2], [3, 4]]]), None),
])

def test_format_box_prompt(polygon, expected):
    result = format_box_prompt(polygon)

    if expected is None:
        assert result is None

    else:
        np.testing.assert_array_almost_equal(result, np.array(expected, dtype = np.float32))