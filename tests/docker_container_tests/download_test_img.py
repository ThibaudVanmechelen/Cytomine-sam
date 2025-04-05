"""Module to download the test image for the mock requests."""

from cytomine import Cytomine
from cytomine.models import ImageInstance

from src.config import get_settings


settings = get_settings()

with Cytomine(settings.keys['host'], settings.keys['public_key'],
              settings.keys['private_key'], verbose = False):

    img = ImageInstance().fetch(27663330)
    img.download(dest_pattern = "./img.jpg", max_size = None)
