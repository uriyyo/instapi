from collections import deque
from contextvars import ContextVar
from dataclasses import dataclass
from functools import partial, wraps
from hashlib import md5
from itertools import chain
from pathlib import Path
from time import time
from typing import Any, Callable, Deque, Dict, Optional, Tuple, TypeVar

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


CACHED_TIME = ContextVar("CACHED_TIME", default=60)
CacheKey = Tuple[Tuple, Tuple]

T = TypeVar("T")


@dataclass
class _CacheInfo:
    cache: Dict[CacheKey, Any]
    keys: Deque[Tuple[CacheKey, float]]


def cached(func: Callable[..., T]) -> Callable[..., T]:
    cache: Dict[CacheKey, Any] = {}
    keys: Deque[Tuple[CacheKey, float]] = deque()

    def _delete_expired_keys() -> None:  # pragma: no cover
        while keys:
            key, expired = keys[0]

            if expired > time():
                break

            keys.popleft()
            del cache[key]

    def _add_key(key: CacheKey) -> None:
        keys.append((key, time() + CACHED_TIME.get()))

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        _delete_expired_keys()

        key: CacheKey = (args, tuple(kwargs.items()))

        if key not in cache:
            cache[key] = func(*args, **kwargs)
            _add_key(key)

        return cache[key]

    wrapper.info: Callable[..., _CacheInfo] = partial(_CacheInfo, cache, keys)  # type: ignore

    return wrapper


__all__ = [
    "CACHED_TIME",
    "cached",
    "get_from_cache",
    "write_to_cache",
]
