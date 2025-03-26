import pytest
import numpy as np

from src.api.models.model import *
from src.utils.convert_geojson import *

@pytest.mark.parametrize("polygon, expected", [
    (GeoJSONPolygon([[[1, 2], [3, 2], [3, 4], [1, 4], [1, 2]]]), [1, 2, 3, 4]),
    (GeoJSONPolygon([[[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]]), [0, 0, 0, 0]),
    (GeoJSONPolygon([]), None),
    (GeoJSONPolygon([[[1, 2], [3, 2], [3, 4]]]), None),
])

def test_mask_to_geojson_single_polygon():
    mask = np.zeros((10, 10), dtype = np.uint8)
    mask[2:6, 2:6] = 1

    result = mask_to_geojson(mask)

    assert result['type'] == 'Polygon'
    assert len(result['coordinates'][0]) >= 4

def test_mask_to_geojson_multi_polygon():
    mask = np.zeros((20, 20), dtype = np.uint8)

    mask[2:6, 2:6] = 1
    mask[10:14, 10:14] = 1

    result = mask_to_geojson(mask)

    assert result['type'] == 'MultiPolygon'
    assert len(result['coordinates']) == 2

@pytest.mark.parametrize("mask_input", [
    np.zeros((10, 10), dtype = np.uint8),
    np.zeros((10, 10), dtype = np.float32),
])

def test_mask_to_geojson_empty(mask_input):
    result = mask_to_geojson(mask_input)
    assert result is None