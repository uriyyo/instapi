from typing import TYPE_CHECKING

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Media

if TYPE_CHECKING:
    from instapi.models import User


@dataclass(frozen=True)
class Comment(Media):
    text: str
    user: 'User'

    def like(self):
        client.comment_like(self.pk)

    def unlike(self):
        client.comment_unlike(self.pk)


__all__ = [
    'Comment',
]
