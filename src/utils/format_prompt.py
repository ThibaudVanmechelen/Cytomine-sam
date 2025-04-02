import numpy as np

from typing import List
from api.models.model import GeoJSONPoint, GeoJSONPolygon


def format_point_prompt(points_data: List[GeoJSONPoint]):
    """
    Function to format the point prompts from the GeoJSON format to the SAM format.

    Args:
        (points_data: List[GeoJSONPoint]): the list of point prompts.

    Returns:
        (np.ndarray): Returns the formatted point prompt coordinates.
        (np.ndarray): Returns the formatted point prompt labels.
    """
    if not points_data:
        return None, None

    point_coords = np.array([pt.coordinates for pt in points_data], dtype = np.int32)
    point_labels = np.array([pt.properties.label for pt in points_data], dtype = np.int32)

    return point_coords, point_labels


def format_box_prompt(box: GeoJSONPolygon):
    """
    Function to format the box prompt from the GeoJSON format to the SAM format.

    Args:
        (box: GeoJSONPolygon): the box prompt.

    Returns:
        (np.ndarray): Returns the formatted box prompt.
    """
    if not box.coordinates or len(box.coordinates[0]) != 5:
        return None

    coords = np.array(box.coordinates[0][:4], dtype = np.int32)

    x_min = np.min(coords[:, 0])
    y_min = np.min(coords[:, 1])
    x_max = np.max(coords[:, 0])
    y_max = np.max(coords[:, 1])

    return np.array([x_min, y_min, x_max, y_max], dtype = np.int32)