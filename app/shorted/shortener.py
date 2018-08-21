from typing import Optional
from hashlib import md5

from sqlalchemy.engine import Connectable

from shorted.algorithms import base62
from shorted.queries import maybe_get_url_by_key, probably_upsert_short_url


class Shortener:

    def __init__(self, db: Connectable) -> None:
        self._db = db

    def create_short_url(self, original_url: str) -> Optional[str]:
        key = create_key(original_url)
        if probably_upsert_short_url(
            self._db,
            key,
            original_url,
        ):
            return f'http://shorted.com/{key}'
        else:
            return None

    def get_original_url(self, key: str) -> Optional[str]:
        url = maybe_get_url_by_key(
            self._db,
            key,
        )
        return url


class TestShortener:

    def __init__(self) -> None:
        self._db: Connectable = {}

    def create_short_url(self, original_url: str) -> str:
        key = create_key(original_url)
        self._db[key] = original_url
        return f'http://shorted.com/{key}'

    def get_original_url(self, key: str) -> str:
        original_url = self._db[key]
        return original_url


def create_key(original_url: str) -> str:
    algorithm = md5()
    algorithm.update(original_url.encode())
    hash_as_int = int(algorithm.hexdigest(), 16)
    return base62(hash_as_int)[:10]
