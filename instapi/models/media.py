from dataclasses import dataclass
from typing import cast

from ..client import client
from ..types import StrDict
from .base import Entity


@dataclass(frozen=True)
class Media(Entity):
    def _media_info(self) -> StrDict:
        items, *_ = client.media_info(self.pk)["items"]
        return cast(StrDict, items)

    def comment(self, text: str) -> None:
        client.post_comment(self.pk, text)


__all__ = [
    "Media",
]
