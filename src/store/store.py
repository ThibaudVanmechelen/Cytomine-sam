from typing import Optional
from redis import Redis  # type: ignore
from pathlib import Path

import time


class Store:
    """A class for managing key-value storage using Redis."""
    def __init__(
        self,
        storage_name: str,
        redis: Redis,
        index_name: str = "index",
        ttl: int = 7800 # 2h10
    ) -> None:
        """
        Store initialisation.

        Args:
            data_path (str): The path to the data source.
            storage_name (str): The name of the storage.
            redis (Redis): An instance of the Redis client.
            index_name (str, optional): The name of the index.
        """
        self.storage_name = storage_name
        self.index_name = index_name
        self.redis = redis
        self.ttl = ttl

        self.prefix = f"{self.storage_name}:{self.index_name}"

    def get(self, key: str) -> Optional[str]:
        """
        Retrieves the value associated with the given key.

        Args:
            key (str): The key whose value is to be retrieved.

        Returns:
            Optional[str]: The value for the given key, or None if it does not exist.
        """
        value = self.redis.get(f"{self.prefix}:{key}")

        return value.decode("UTF-8") if value is not None else None

    def set(self, key: str, value: str) -> None:
        """
        Sets the value for the specified key in the Redis database.

        Args:
            key (str): The key for which the value is to be set.
            value (str): The value to be set for the specified key.
        """
        full_key = f"{self.prefix}:{key}"
        self.redis.setex(full_key, self.ttl, value)
        self.redis.setex(f"{full_key}:timestamp", self.ttl, str(int(time.time())))

    def last(self) -> int:
        """
        Retrieves the value of the key "last_id".

        Returns:
            int: The value of the "last_id" key, or 0 if the key does not exist.
        """
        return int(self.get("last_id") or "0")

    def contains(self, key: str) -> bool:
        """
        Checks if a value exists for the given key.

        Args:
            key (str): The key to check for existence.

        Returns:
            bool: True if a value exists for the key, False otherwise.
        """
        return self.get(key) is not None

    def remove(self, key: str) -> None:
        """
        Deletes the value associated with the specified key from the Redis database.

        Args:
            key (str): The key to be deleted.
        """
        self.redis.delete(f"{self.prefix}:{key}")

    def get_ttl(self, key: str) -> Optional[int]:
        ttl = self.redis.ttl(f"{self.prefix}:{key}")

        if ttl >= 0:
            return ttl

        return None

    def update_ttl(self, key: str) -> bool:
        result = self.redis.expire(f"{self.prefix}:{key}",self.ttl)

        return result
    

def cleanup_cached_files(store: Store, tmp_dir: str = "/tmp", threshold_sec: int = 7200):
    now = int(time.time())
    keys = store.redis.keys(f"{store.prefix}:*:timestamp")

    for timestamp_key in keys:
        try:
            timestamp_str = store.redis.get(timestamp_key)
            if not timestamp_str:
                continue

            created_time = int(timestamp_str)
            age = now - created_time

            if age > threshold_sec:
                base_key = timestamp_key.replace(":timestamp", "")
                image_id = base_key.split(":")[-1]
                file_path = Path(tmp_dir) / f"cytomine_{image_id}.jpg"

                if file_path.exists():
                    file_path.unlink()
                    print(f"[CLEANUP] Deleted file: {file_path}")

                store.remove(image_id)
                store.redis.delete(timestamp_key)

        except Exception as e:
            print(f"[CLEANUP ERROR] Failed on key {timestamp_key}: {e}")