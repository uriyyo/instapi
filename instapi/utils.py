from functools import partial
from typing import (
    Callable,
    Iterable,
    List,
    Optional,
    TypeVar,
)
from uuid import uuid1

T = TypeVar('T')


def process_many(
        fetcher: Callable,
        pk: Optional[int] = None,
        with_rank_token: bool = False,
) -> Iterable:
    next_max_id = None

    if pk is not None:
        fetcher = partial(fetcher, pk)

    if with_rank_token:
        fetcher = partial(fetcher, rank_token=str(uuid1()))

    while True:
        if next_max_id is not None:
            result = fetcher(max_id=next_max_id)
        else:
            result = fetcher()

        yield result

        if not result.get('next_max_id'):
            break

        next_max_id = result['next_max_id']


def limited(iterable: Iterable[T], limit: Optional[int] = None) -> Iterable[T]:
    if limit is None:
        yield from iterable
    else:
        yield from (i for _, i in zip(range(limit), iterable))


def to_list(iterable: Iterable[T], limit: Optional[int] = None) -> List[T]:
    return [*limited(iterable, limit=limit)]


__all__ = [
    'process_many',
    'limited',
    'to_list',
]
