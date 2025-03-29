from box import Box
from tomli import load

def load_config(config_path : str):
    """Loads a config file in toml format. Returns a dictionary with the config values."""
    with open(config_path, "rb") as f:
        config = load(f)

    return Box(config)