"""Module to handle the smart fetching of the point annotations."""

from typing import List, Dict, Any

from shapely import wkt
from shapely.geometry import Point, Polygon, shape

from cytomine import Cytomine
from cytomine.models import AnnotationCollection

from src.config import Settings


def filter_point_annotations_within_polygon(
        box: Polygon,
        annotations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
    """
    Function to filter an array of annotations to only keep the point annotations that
    are inside of the box polygon.

    Args:
        (box: Polygon): the box in which the points are kept.
        (annotations: List[Dict[str, Any]]): the annotations to filter.

    Returns:
        (List[Dict[str, Any]]): Returns the point inside the box.
    """
    return [
        ann for ann in annotations
        if isinstance(ann["geometry"], Point) and box.contains(ann["geometry"])
    ]


def fetch_included_annotations(
        image_id: int,
        user_id: int,
        geometry: Dict[str, Any],
        settings: Settings,
        delete_annotations: bool = True
    ) -> List[Dict[str, Any]]:
    """
    Function to fetch the user annotations that are included in the geometry.
    The fetched annotations are only point annotations that are included in the
    box geometry. This function can optionally delete those point annotations if
    they are not useful anymore.

    Args:
        (image_id: int): the id of the image to fetch the annotations from.
        (user_id: int): the id of the user from whom annotations are fetched.
        (geometry: Dict[str, Any]): the box geometry for this image.
        (settings: Settings): the settings.
        (delete_annotations: bool): whether to delete the point annotations afterwards.

    Returns:
        (List[Dict[str, Any]]): Returns the point prompts formatted as GeoJSON.
    """
    box = shape(geometry["geometry"])

    with Cytomine(settings.keys['host'], settings.keys['public_key'],
                  settings.keys['private_key'], verbose = False):

        annotations = AnnotationCollection()
        annotations.image = image_id
        annotations.user = user_id
        annotations.showWKT = True
        annotations.showMeta = True

        annotations.fetch()

        annotation_list = []
        for annotation in annotations:
            annotation_geometry = wkt.loads(annotation.location)
            annotation_list.append({
                "id": annotation.id,
                "geometry": annotation_geometry
            })

        filtered_annotation_list = filter_point_annotations_within_polygon(box, annotation_list)
        annotation_id_list = [ann["id"] for ann in filtered_annotation_list]

        if delete_annotations:
            for ann in annotations:
                if ann.id in annotation_id_list:
                    ann.delete()

    return annotations_to_geojson_features(filtered_annotation_list)


def annotations_to_geojson_features(annotations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Function to convert the annotations to the GeoJSON format.

    Args:
        (annotations: List[Dict[str, Any]]): the annotations to convert.

    Returns:
        (List[Dict[str, Any]]): Returns the annotations in GeoJSON format.
    """
    features = []

    for ann in annotations:
        geom = ann["geometry"]

        if isinstance(geom, Point):
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [geom.x, geom.y]
                },
                "properties": {
                    "label": 1
                }
            })

    return features
