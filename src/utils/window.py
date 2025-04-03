"""Module to extract a patch of the original WSI image."""

import os
import tempfile
import matplotlib.pyplot as plt

from cytomine.models.image import ImageInstance


def load_cytomine_window_image(obj: ImageInstance, x: int, y: int, w: int, h: int):
    """
    Function to download the cropped part of the original WSI.

    Args:
        (obj: ImageInstance): the original WSI Image Instance.
        (x: int): the offset along the x-axis.
        (y: int): the offset along the y-axis.
        (w: int): the width of the cropped part.
        (h: int): the height of the cropped part.

    Returns:
        (np.ndarray): Returns the cropped part of the image
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, "window.jpg")
        obj.window(x, y, w, h, dest_pattern = tmp_path)

        try:
            return plt.imread(tmp_path)

        except Exception as e:
            print(f"Failed to read the cropped image: {e}")
            return None
