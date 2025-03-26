import cv2
import numpy as np
from math import floor

ZOOM_OUT_FACTOR = 2.0
MAX_SIZE = 1024

def get_localisation_of_annotation(box: np.ndarray):
    width = floor(box[2] - box[0])
    height = floor(box[3] - box[1])

    return width, height, floor(box[0]), floor(box[3]) # bottom left referential here


def get_annotation_size(img_width: int, img_height: int, width: int, height: int) -> int:
    annotation_size = max(width, height)

    return min(floor(annotation_size * ZOOM_OUT_FACTOR), img_width, img_height)


def get_roi_around_annotation(img: np.ndarray, box: np.ndarray):
    img_height = img.shape[0]
    img_width = img.shape[1]

    annotation_width, annotation_height, x, y = get_localisation_of_annotation(box)
    size = get_annotation_size(img_width, img_height, annotation_width, annotation_height)

    h = (size - annotation_width) / 2 
    v = (size - annotation_height) / 2

    x = floor(x - h)
    y = floor(img_height - y - v)

    x = min(x, img_width - size)
    y = min(y, img_height - size)

    x = max(0, x)
    y = max(0, y)

    return x, y, size, size


def resize_to_max_size_cv2(img: np.ndarray, max_size: int):
    height, width = img.shape[:2]
    max_original = max(width, height)

    if max_original <= max_size:
        return img, -1, -1

    scale = max_size / max_original
    new_width = int(width * scale)
    new_height = int(height * scale)

    resized_img = cv2.resize(img, (new_width, new_height), interpolation = cv2.INTER_AREA)

    return resized_img, width, height


def extract_img_region(img: np.ndarray, box: np.ndarray):
    x, y, size, _ = get_roi_around_annotation(img, box)
    cropped_img = img[y : y + size, x : x + size]

    resized_cropped_img, width, height = resize_to_max_size_cv2(cropped_img, MAX_SIZE)

    return resized_cropped_img, x, y, width, height


