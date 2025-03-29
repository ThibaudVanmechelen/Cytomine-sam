"""Environment parameters"""

import torch
from pydantic_settings import BaseSettings
from utils.config import load_config


class Settings(BaseSettings):
    """Configurable settings."""

    # Database
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    ttl: int = 7200

    # Deep learning model
    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config: str = "/configs/sam2.1_hiera_b+.yaml"
    checkpoint: str = "/weights/weights.pt"

    keys = load_config('../keys.toml')


def get_settings() -> Settings:
    return Settings()