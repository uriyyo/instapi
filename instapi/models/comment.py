from __future__ import annotations

from typing import TYPE_CHECKING

from ..client import client
from .media import Media

if TYPE_CHECKING:
    from instapi.models import User  # pragma: no cover


class Comment(Media):
    """
    This class represents a comment in Instagram
    """

    text: str
    user: User

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
    "Comment",
]
