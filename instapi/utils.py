from functools import wraps
from typing import (
    Callable,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
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
        yield from (i for i, _ in zip(iterable, range(limit)))


def fetcher(iter_func: Union[Callable[..., Iterable[T]], classmethod]):
    if isinstance(iter_func, classmethod):
        iter_func: Iterable[T] = iter_func.__func__

    def decorator(func):
        @wraps(func)
        def wrapper(self, limit: Optional[T] = None) -> List[T]:
            return [*limited(iter_func(self), limit)]

        return wrapper

    return decorator


__all__ = [
    'process_many',
    'limited',
    'fetcher',
]
