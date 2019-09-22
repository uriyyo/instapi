from typing import cast

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Entity
from instapi.types import StrDict


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> StrDict:
        items, *_ = client.media_info(self.pk)['items']
        return cast(StrDict, items)

    def comment(self, text: str) -> None:
        client.post_comment(self.pk, text)


__all__ = [
    'Media',
]
