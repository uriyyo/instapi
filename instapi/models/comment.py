from typing import TYPE_CHECKING

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Media

if TYPE_CHECKING:
    from instapi.models import User  # pragma: no cover


@dataclass(frozen=True)
class Comment(Media):
    """
    This class represents a comment in Instagram
    """
    text: str
    user: 'User'

    def like(self) -> None:
        """
        Like comment

        :return: None
        """
        client.comment_like(self.pk)

    def unlike(self) -> None:
        """
        Unlike comment

        :return: None
        """
        client.comment_unlike(self.pk)


__all__ = [
    'Comment',
]
