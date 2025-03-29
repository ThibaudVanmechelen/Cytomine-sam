from pydantic import BaseModel
from typing import List, Optional, Literal
from fastapi import Request

class GeoJSONPolygon(BaseModel):
    """
        {
            "type": "Polygon", 
            "coordinates": [
                [
                    [x1, y1],
                    [x2, y2],
                    [x3, y3],
                    [x4, y4],
                    [x1, y1]        // this is for a Box
                ]
            ]
        }
    """
    type: Literal["Polygon"]
    coordinates: List[List[List[int]]]


class PointProperties(BaseModel):
    label: Literal[0, 1]  # 1 = positive, 0 = negative


class GeoJsonPoint(BaseModel):
    """
        {
            "type": "Point", 
            "coordinates": [x, y]
            "properties": {
                "label": 1          // 1 for positive point and 0 for negative point
            }
        }
    """
    type: Literal["Point"]
    coordinates: List[int]
    properties: PointProperties


class SegmentationFromIdRequest(BaseModel):
    request: Request
    image_id: int
    geometry: GeoJSONPolygon
    points: Optional[List[GeoJsonPoint]] = None # Optional