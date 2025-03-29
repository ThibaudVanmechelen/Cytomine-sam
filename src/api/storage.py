from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from src.store.store import *
from src.utils.store_utils import get_redis

from cytomine import Cytomine
from cytomine.models import ImageInstance

from src.config import Settings, get_settings
from pathlib import Path

router = APIRouter()

@router.post("/prediction/upload")
async def precache_image(
    image_id: str,
    background_tasks: BackgroundTasks,
    store: Store = Depends(get_redis),
    settings: Settings = Depends(get_settings)
):
    try:
        if not store.contains(image_id):
            background_tasks.add_task(cache_image, image_id, store, settings)

        return {"status": "caching_started"}

    except HTTPException as e:
        raise e

def cache_image(image_id: str, store: Store, settings: Settings):
    path = Path(f"/tmp/cytomine_{image_id}.jpg")

    with Cytomine(settings.keys['host'], settings.keys['public_key'], settings.keys['private_key'], verbose = False) as cytomine:
        img = ImageInstance().fetch(image_id)
        img.download(dest_pattern = str(path), max_size = None)

    store.set(image_id, str(path))