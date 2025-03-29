import cv2
import numpy as np


def post_process_segmentation_mask(mask : np.ndarray, opening_kernel_size : int = 10, closing_kernel_size : int = 20, blur_size : int = 21, do_gaussian_blur : bool = False):
    if mask.dtype != np.uint8:
        mask = (mask * 255).astype(np.uint8)

    opening_kernel = np.ones((opening_kernel_size, opening_kernel_size), np.uint8)
    opened_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, opening_kernel)

    closing_kernel = np.ones((closing_kernel_size, closing_kernel_size), np.uint8)
    temp_mask = cv2.morphologyEx(opened_mask, cv2.MORPH_CLOSE, closing_kernel)

    if do_gaussian_blur:
        _, temp_mask = cv2.threshold(cv2.GaussianBlur(temp_mask, (blur_size, blur_size), 0), 127, 255, cv2.THRESH_BINARY)

    temp_mask = filter_mask_by_size(temp_mask)

    return temp_mask


def filter_mask_by_size(mask : np.ndarray, area_thresh_percentage : float = 0.1):
    """ Function to clean the mask, this function cleans the mask by removing connected area which are less than 10% of the biggest part of the mask """
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity = 8)
    areas = stats[:, cv2.CC_STAT_AREA]

    if len(areas) <= 1: # there is just background here, empty mask
        return np.zeros_like(mask)

    max_area = np.max(areas[1:]) # max area is the principal mask
    min_area = area_thresh_percentage * max_area # min area that an element should have

    filtered_mask = np.zeros_like(mask)
    for label in range(1, num_labels):
        if areas[label] >= min_area:
            filtered_mask[labels == label] = 255

    return filtered_mask


def upscale_mask(mask: np.ndarray, init_shape: tuple):
    if init_shape[0] == -1 or init_shape[1] == -1:
        return mask

    return cv2.resize(mask, (init_shape[1], init_shape[0]), interpolation = cv2.INTER_NEAREST) # cv2.resize takes tuple (width, height)
