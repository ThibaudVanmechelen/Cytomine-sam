import numpy as np
from typing import List
from api.models.model import GeoJsonPoint, GeoJSONPolygon

def format_point_prompt(points_data: List[GeoJsonPoint]):
    if not points_data:
        return None, None

    point_coords = np.array([pt.coordinates for pt in points_data], dtype = np.float32)
    point_labels = np.array([pt.properties.label for pt in points_data], dtype = np.int32)

    return point_coords, point_labels


def format_box_prompt(box: GeoJSONPolygon):
    if not box.coordinates or len(box.coordinates[0]) != 5:
        return None

    coords = np.array(box.coordinates[0][:4], dtype = np.float32)

    x_min = np.min(coords[:, 0])
    y_min = np.min(coords[:, 1])
    x_max = np.max(coords[:, 0])
    y_max = np.max(coords[:, 1])

    return np.array([x_min, y_min, x_max, y_max], dtype = np.float32)