import pytest
import numpy as np

from src.utils.postprocess import *

def test_post_process_segmentation_mask_basic():
    mask = np.zeros((50, 50), dtype = np.uint8)
    mask[20:30, 20:30] = 255

    processed = post_process_segmentation_mask(mask)

    assert processed.shape == mask.shape
    assert processed.dtype == np.uint8
    assert np.any(processed > 0)


def test_post_process_segmentation_mask_with_blur():
    mask = np.zeros((50, 50), dtype = np.uint8)
    mask[20:30, 20:30] = 1

    processed = post_process_segmentation_mask(mask.astype(np.float32))

    assert processed.shape == mask.shape
    assert processed.dtype == np.uint8
    assert np.any(processed > 0)


def test_filter_mask_by_size():
    mask = np.zeros((100, 100), dtype = np.uint8)

    cv2.rectangle(mask, (10, 10), (30, 30), 255, -1)
    cv2.rectangle(mask, (60, 60), (62, 62), 255, -1)

    filtered = filter_mask_by_size(mask)

    assert filtered[60, 60] == 0
    assert filtered[20, 20] == 255