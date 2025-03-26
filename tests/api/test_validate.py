import pytest
from src.api.models.validate import *


def test_validate_box_valid():
    polygon = GeoJSONPolygon([[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]])

    try:
        validate_box(polygon)

    except HTTPException:
        pytest.fail("Unexpected HTTPException for valid box")


def test_validate_box_not_closed():
    polygon = GeoJSONPolygon([[[0, 0], [1, 0], [1, 1], [0, 1], [1, 1]]])

    with pytest.raises(HTTPException) as exc:
        validate_box(polygon)

    assert "Box must be closed" in str(exc.value.detail)


def test_validate_box_wrong_corners():
    polygon = GeoJSONPolygon([[[0, 0], [2, 0], [2, 2], [1, 1], [0, 0]]])

    with pytest.raises(HTTPException) as exc:
        validate_box(polygon)

    assert "Box corners do not form a proper rectangle" in str(exc.value.detail)


def test_validate_box_not_axis_aligned():
    polygon = GeoJSONPolygon([[[0, 0], [0.5, 0], [0.5, 1], [0, 1], [0, 0]]])

    with pytest.raises(HTTPException) as exc:
        validate_box(polygon)

    assert "Box must be an axis-aligned rectangle" in str(exc.value.detail)


def test_validate_box_wrong_length():
    polygon = GeoJSONPolygon([[[0, 0], [1, 0], [1, 1], [0, 1]]])

    with pytest.raises(HTTPException) as exc:
        validate_box(polygon)
    
    assert "Box must have 5 coordinates" in str(exc.value.detail)


def test_validate_coordinates_valid():
    point = GeoJsonPoint([10, 20], 1)

    try:
        validate_coordinates(point)

    except HTTPException:
        pytest.fail("Unexpected HTTPException for valid point")


def test_validate_coordinates_invalid():
    point = GeoJsonPoint([10], 1)

    with pytest.raises(HTTPException) as exc:
        validate_coordinates(point)

    assert "Point must have 2 coordinates" in str(exc.value.detail)