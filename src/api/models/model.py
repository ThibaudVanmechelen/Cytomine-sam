from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SegmentationRequest(BaseModel):
    """
    Class to represent the request for segmentation.
    Example:
        {
            "image_id": 42,
            "geometry": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[10, 10], [20, 10], [20, 20], [10, 20], [10, 10]]]
                },
                "properties": {}
            },
            "points": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [15, 15]
                    },
                    "properties": {
                        "label": 1
                    }
                }
            ]
        }
    """
    image_id: int
    geometry: Dict[str, Any]
    points: Optional[List[Dict[str, Any]]] = None  # List of GeoJSON Feature that correspond to points.