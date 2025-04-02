import pytest
from fastapi import HTTPException

from src.api.models.validate import validate_box_feature, validate_point_feature


def test_valid_box():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[1, 1], [4, 1], [4, 3], [1, 3], [1, 1]]]
        }
    }

    assert validate_box_feature(feature) is None

def test_box_invalid_type():
    feature = {"type": "Invalid", "geometry": {}}

    with pytest.raises(HTTPException, match = "Geometry must be a GeoJSON Feature"):
        validate_box_feature(feature)

def test_box_not_polygon():
    feature = {"type": "Feature", "geometry": {"type": "Point"}}

    with pytest.raises(HTTPException, match = "Geometry must be a Polygon"):
        validate_box_feature(feature)

def test_box_missing_coordinates():
    feature = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}}

    with pytest.raises(HTTPException, match = "Polygon must have coordinates"):
        validate_box_feature(feature)

def test_box_not_closed():
    feature = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[1, 1], [4, 1], [4, 3], [1, 3]]]}}

    with pytest.raises(HTTPException, match = "Box must have 5 coordinates"):
        validate_box_feature(feature)

def test_box_open_shape():
    feature = {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[1, 1], [4, 1], [4, 3], [1, 3], [2, 2]]]}}

    with pytest.raises(HTTPException, match = "Box must be closed"):
        validate_box_feature(feature)

def test_box_not_axis_aligned():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[1, 1], [3, 2], [2, 4], [0, 3], [1, 1]]]
        }
    }

    with pytest.raises(HTTPException, match = "Box must be an axis-aligned rectangle"):
        validate_box_feature(feature)

def test_box_incorrect_rectangle():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[1, 1], [4, 1], [4, 2], [1, 4], [1, 1]]]
        }
    }

    with pytest.raises(HTTPException, match = "Box corners do not form a proper rectangle"):
        validate_box_feature(feature)


def test_valid_point():
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [1, 2]},
        "properties": {"label": 1}
    }

    assert validate_point_feature(feature) is None

def test_point_invalid_type():
    feature = {"type": "Invalid", "geometry": {}}

    with pytest.raises(HTTPException, match = "Point must be a GeoJSON Feature"):
        validate_point_feature(feature)

def test_point_wrong_geometry():
    feature = {"type": "Feature", "geometry": {"type": "Polygon"}}

    with pytest.raises(HTTPException, match = "Point geometry must be of type Point"):
        validate_point_feature(feature)

def test_point_wrong_coords():
    feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1]}, "properties": {"label": 0}}

    with pytest.raises(HTTPException, match = "Point must have exactly 2 coordinates"):
        validate_point_feature(feature)

def test_point_missing_label():
    feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "properties": {}}

    with pytest.raises(HTTPException, match = "Point must have a 'label' property"):
        validate_point_feature(feature)

def test_point_invalid_label():
    feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "properties": {"label": 2}}

    with pytest.raises(HTTPException, match = "Point must have a 'label' property with value 0 or 1"):
        validate_point_feature(feature)