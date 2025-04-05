"""Module to test docker container for the API."""

from typing import Union

import random
import httpx

from PIL import Image, ImageDraw
from shapely.geometry import shape


URL = "http://localhost:8000/prediction"

mock_requests = [
    {
        "image_id": 27663330,
        "geometry": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[42872, 124110], [43400, 124110], [43400, 123655], 
                                 [42872, 123655], [42872, 124110]]]
            },
            "properties": {}
        },
        "points": []
    },
    {
        "image_id": 27663330,
        "geometry": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[43425, 121705], [45225, 121705], [45225, 120800], 
                                 [43425, 120800], [43425, 121705]]]
            },
            "properties": {}
        },
        "points": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [44471, 121313]
                },
                "properties": {
                    "label": 1
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [44955, 121030]
                },
                "properties": {
                    "label": 1
                }
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [43699, 121411]
                },
                "properties": {
                    "label": 1
                }
            }
        ]
    }
]

responses = []
for i, payload in enumerate(mock_requests):
    response = httpx.post(URL, json = payload)
    print(f"Response for request {i + 1}: {response.status_code}")
    print(response.json())

    responses.append(response)

IMAGE_PATH = "./img.jpg"
original = Image.open(IMAGE_PATH).convert("RGB")
image_height = original.height
draw = ImageDraw.Draw(original)

def random_bright_color() -> tuple:
    """Function to select a random color."""
    return tuple(random.choices(range(128, 256), k = 3))

def flip_y(y: Union[float, int]) -> Union[float, int]:
    """Function to change the y-axis direction."""
    return image_height - y

def transform_coords(coords: list) -> list:
    """Function to apply the y-axis transformation to all coords."""
    return [(x, flip_y(y)) for x, y in coords]

for i, response in enumerate(responses):
    geojson_feature = response.json()
    geom = shape(geojson_feature["geometry"])

    color = random_bright_color()

    if geom.geom_type == "Polygon":
        coords_ = transform_coords(list(geom.exterior.coords))
        draw.polygon(coords_, outline = color, width = 4)

    elif geom.geom_type == "MultiPolygon":
        for poly in geom.geoms:
            coords_ = transform_coords(list(poly.exterior.coords))
            draw.polygon(coords_, outline = color, width = 4)

OUTPUT_PATH = "overlay_result.jpg"
original.save(OUTPUT_PATH)

print(f"Saved overlay image to {OUTPUT_PATH}")
