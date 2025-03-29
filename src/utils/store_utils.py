from fastapi import Depends, HTTPException
from redis import Redis, RedisError  # type: ignore

from src.config import Settings, get_settings
from src.store.store import Store


def get_redis(settings: Settings = Depends(get_settings)) -> Redis:
    """
    Get the Redis client.

    Args:
        settings (Settings): The database settings.

    Returns:
        Redis: The Redis client.
    """
    try:
        return Redis(host = settings.host, port = settings.port, db = settings.db)
    
    except RedisError as e:
        raise HTTPException(status_code = 500, detail = f"Redis connection error: {str(e)}")
    

def get_store(redis: Redis = Depends(get_redis)):
    """
    Instantiate a Store object.

    Args:
        redis (Redis): An instance of the Redis client.

    Returns:
        Store: An instance of the Store.
    """
    return Store("default_store", redis, "index", ttl = 7800)