import cv2
import numpy as np


def mask_to_geojson(mask: np.ndarray, offset_x: int = 0, offset_y: int = 0):
    """
    Function to convert the mask to a GeoJSON taking into account the offset due
    to the manipulation of WSIs.

    Args:
        (mask: np.ndarray): the mask.
        (offset_x: int): the offset along the x-axis.
        (offset_y: int): the offset along the y-axis.

    Returns:
        (dict): Returns the structure as a GeoJSON
    """
    mask = (mask > 0).astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    polygons = []
    for contour in contours:
        if len(contour) >= 3: # because the polygon must at least have 3 points
            coords = contour.squeeze()

            if coords.ndim != 2:
                continue

            coords = coords + np.array([offset_x, offset_y])
            coords = coords.tolist()

            if coords[0] != coords[-1]:
                coords.append(coords[0])

            polygons.append(coords)

    if not polygons:
        return None

    if len(polygons) == 1:
        geojson = {
            "type": "Polygon",
            "coordinates": [polygons[0]]
        }

    else:
        geojson = {
            "type": "MultiPolygon",
            "coordinates": [[poly] for poly in polygons]
        }

    return geojson