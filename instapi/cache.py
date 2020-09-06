from hashlib import md5
from itertools import chain
from pathlib import Path
from typing import Optional

from instagram_private_api.http import ClientCookieJar

from instapi.types import Credentials


def _get_cache_root() -> Path:  # pragma: no cover
    cwd = Path.cwd()

    for p in chain([cwd], cwd.parents):
        cache = p / ".instapi_cache"

        if cache.exists():
            return cache

    return cwd / ".instapi_cache"


_CACHE_ROOT = _get_cache_root()
_CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def _get_hash(credentials: Credentials) -> str:  # pragma: no cover
    return md5(":".join(credentials).encode()).hexdigest()


# TODO: add tests for cache logic
def get_from_cache(credentials: Credentials) -> Optional[bytes]:  # pragma: no cover
    cache = _CACHE_ROOT / _get_hash(credentials)
    return cache.read_bytes() if cache.exists() else None


def write_to_cache(credentials: Credentials, cookie: ClientCookieJar) -> None:  # pragma: no cover
    cache = _CACHE_ROOT / _get_hash(credentials)
    cache.write_bytes(cookie.dump())


__all__ = ["get_from_cache", "write_to_cache"]
