"""Environment parameters"""

import torch
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurable settings."""

    # Deep learning model
    device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config: str = "/configs/sam2.1_hiera_b+.yaml"
    checkpoint: str = "/weights/weights.pt"


def get_settings() -> Settings:
    return Settings()