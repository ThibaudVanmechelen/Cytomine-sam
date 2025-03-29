import matplotlib.pyplot as plt
import tempfile
import os
from cytomine.models.image import ImageInstance
from cytomine import Cytomine

from src.store.store import Store
from src.config import Settings

def load_cytomine_window_image(obj, x, y, w, h):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = os.path.join(tmpdir, "window.jpg")

        window = obj.window(x, y, w, h, dest_pattern = tmp_path)
        if not window:
            raise RuntimeError("Failed to fetch image window")

        return plt.imread(tmp_path).copy()
    

def download_and_cache_image(image_id: int, store: Store, settings: Settings):
    local_path = f"/tmp/cytomine_{image_id}.jpg"

    with Cytomine(settings.keys["host"], settings.keys["public_key"], settings.keys["private_key"], verbose = False) as cytomine:
        img = ImageInstance().fetch(image_id)
        img.download(dest_pattern = local_path, max_size = None)

    store.set(image_id, local_path)

    return local_path