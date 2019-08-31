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

    kwargs = {'rank_token': str(uuid1())} if with_rank_token else {}
    args = (pk,) if pk is not None else ()

    while True:
        result = fetcher(
            *args,
            **kwargs,
            **({'max_id': next_max_id} if next_max_id else {}),
        )

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
