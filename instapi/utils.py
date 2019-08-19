from typing import (
    Callable,
    Iterable,
)
from uuid import uuid1


def process_many(fetcher: Callable, pk: int, *, with_rank_token: bool = False) -> Iterable:
    next_max_id = None

    while True:
        result = fetcher(
            pk,
            **({'rank_token': str(uuid1())} if with_rank_token else {}),
            **({'max_id': next_max_id} if next_max_id else {}),
        )

        yield result

        if not result.get('next_max_id'):
            break

        next_max_id = result['next_max_id']
