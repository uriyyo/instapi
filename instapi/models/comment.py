from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, List, Optional

from ..client import client
from ..utils import to_list
from .media import Media

if TYPE_CHECKING:
    from instapi.models import User  # pragma: no cover


@dataclass(frozen=True)
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


class CommentsBoundMixin:
    pk: int

    def iter_comments(self) -> Iterable[Comment]:
        """
        Create generator for iteration over comments, which was attached to the media

        :return: generator with comments
        """
        for c in client.media_comments_gen(self.pk):
            from instapi.models import User

            yield Comment.create({**c, "user": User.create(c["user"])})

    def comments(self, limit: Optional[int] = None) -> List[Comment]:
        """
        Generate list of comments, which was attached to the media

        :param limit: number of comments, which will be added to the list
        :return: list with comments
        """
        return to_list(self.iter_comments(), limit=limit)


__all__ = [
    "Comment",
    "CommentsBoundMixin",
]
