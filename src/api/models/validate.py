import numpy as np
from model import GeoJSONPolygon, GeoJsonPoint
from fastapi import HTTPException

def validate_box(polygon: GeoJSONPolygon):
    coords = polygon.coordinates[0]

    if len(coords) != 5:
        raise HTTPException(status_code = 400, detail = "Box must have 5 coordinates (4 corners + closing point).")

    if coords[0] != coords[-1]:
        raise HTTPException(status_code = 400, detail = "Box must be closed (first and last coordinate must match).")

    corners = coords[:4]

    x_coords = [pt[0] for pt in corners]
    y_coords = [pt[1] for pt in corners]

    unique_x = sorted(set(x_coords))
    unique_y = sorted(set(y_coords))

    if len(unique_x) != 2 or len(unique_y) != 2:
        raise HTTPException(status_code = 400, detail = "Box must be an axis-aligned rectangle (2 unique x and y values).")

    normal_corners = [[unique_x[0], unique_y[0]], [unique_x[1], unique_y[0]], [unique_x[1], unique_y[1]], [unique_x[0], unique_y[1]]]

    if sorted(map(tuple, corners)) != sorted(map(tuple, normal_corners)):
        raise HTTPException(status_code = 400, detail = "Box corners do not form a proper rectangle.")
    

def validate_coordinates(point: GeoJsonPoint):
    coords = point.coordinates

    if len(coords) != 2:
        raise HTTPException(status_code = 400, detail = "Point must have 2 coordinates.")