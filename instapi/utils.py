from functools import (
    partial,
)
from itertools import chain
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    TypeVar,
)
from uuid import uuid1


T = TypeVar('T')


def fetch_key(source: Dict, key_path: str) -> Any:
    for key in key_path.split('.'):
        if key in source:
            source = source[key]
        else:
            return None

    return source


def process_many(
        fetcher: Callable,
        pk: Optional[int] = None,
        with_rank_token: bool = False,
        key: str = 'max_id',
        key_path: str = 'next_max_id',
) -> Iterable:
    next_value = None

    if pk is not None:
        fetcher = partial(fetcher, pk)

    if with_rank_token:
        fetcher = partial(fetcher, rank_token=str(uuid1()))

    while True:
        if next_value is not None:
            result = fetcher(**{key: next_value})
        else:
            result = fetcher()

        yield result

        next_value = fetch_key(result, key_path)

        if not next_value:
            break


def limited(iterable: Iterable[T], limit: Optional[int] = None) -> Iterable[T]:
    if limit is None:
        yield from iterable
    else:
        if limit < 0:
            raise ValueError('Limited can\'t handle negative numbers')

        yield from (i for _, i in zip(range(limit), iterable))


def to_list(iterable: Iterable[T], limit: Optional[int] = None) -> List[T]:
    return [*limited(iterable, limit=limit)]


def flat(source: List[Iterable[T]]) -> List[T]:
    """
    Unpack list of iterable into single list

    :param source: list of iterable
    :return: unpacked list
    """
    return [*chain.from_iterable(source)]


def join(iterable: Iterable, separator: str = ',') -> str:
    return separator.join(str(s) for s in iterable)


__all__ = [
    'process_many',
    'limited',
    'to_list',
    'flat',
    'join',
]
