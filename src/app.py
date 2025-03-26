"""Segment Anything API"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src import __version__
from sam2 import SAM2ImagePredictor, build_sam2
from src.config import Settings, get_settings
from src.api import prediction

def load_predictor(settings: Settings) -> SAM2ImagePredictor:
    sam2_model = build_sam2(settings.config, settings.checkpoint, device = settings.device)

    return SAM2ImagePredictor(sam2_model)


@asynccontextmanager
async def lifespan(local_app: FastAPI) -> AsyncGenerator[None, None]:
    local_app.state.predictor = load_predictor(get_settings())
    yield


app = FastAPI(
    title = "Cytomine Segment Anything Server",
    description = "Cytomine Segment Anything HTTP API.",
    version = __version__,
    lifespan = lifespan,
    license_info = {
        "name": "Apache 2.0",
        "identifier": "Apache-2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.include_router(router = prediction.router, prefix="/api")