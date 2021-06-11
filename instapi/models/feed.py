from dataclasses import dataclass
from typing import Iterable, List, Optional, cast

from ..cache import cached
from ..client import client
from ..types import StrDict
from ..utils import process_many, to_list
from .comment import CommentsBoundMixin
from .resource import ResourceContainer
from .user import User


@dataclass(frozen=True)
class Feed(CommentsBoundMixin, ResourceContainer):
    """
    This class represent Instagram's feed. It gives opportunity to:
    -   Get posts from feed
    -   Get info about post (comments, which was attached to the post; users, which has liked the post)
    -   Like/Unlike posts
    -   Get media (videos and images) from posts
    """

    like_count: int
    comment_count: int = 0

    @property
    def caption(self) -> str:
        return cast(str, self._media_info()["caption"]["text"])

    @classmethod
    def iter_timeline(cls) -> Iterable["Feed"]:
        """
        Create generator for iteration over posts from feed

        :return: generator with posts from feed
        """
        for result in process_many(client.feed_timeline):
            yield from (
                Feed.create(data["media_or_ad"])
                for data in result["feed_items"]
                if "media_or_ad" in data
            )

    @classmethod
    def timeline(cls, limit: Optional[int] = None) -> List["Feed"]:
        """
        Generate list of posts from feed

        :param limit: number of posts, which will be added to the list
        :return: list with posts from feed
        """
        return to_list(cls.iter_timeline(), limit=limit)

    def _resources(self) -> Iterable["StrDict"]:
        """
        Feed can contain multiple images and videos that located in carousel_media

        :return: source of videos or images
        """
        media_info = self._media_info()
        return media_info.get("carousel_media", [media_info])

    @cached
    def user_tags(self) -> List["User"]:
        """
        Generate list of Users from Feed usertags

        :return: list of Users from usertags
        """
        info = self._media_info()

        if "usertags" not in info:
            return []

        return [User.create(u["user"]) for u in info["usertags"]["in"]]

    def iter_likes(self) -> Iterable["User"]:
        """
        Create generator for iteration over posts from feed

        :return: generator with users, which has liked a post
        """
        for result in process_many(client.media_likers, self.pk):
            yield from map(User.create, result["users"])

    def likes(self, limit: Optional[int] = None) -> List["User"]:
        """
        Generate list of users, which has liked a post

        :param limit: number of users, which will be added to the list
        :return: list with users, which has liked a post
        """
        return to_list(self.iter_likes(), limit=limit)

    def liked_by(self, user: "User") -> bool:
        """
        Check if post was liked by user

        :param user: user for checking
        :return: boolean value
        """
        return any(
            any(user.pk == u["pk"] for u in result["users"])
            for result in process_many(client.media_likers, self.pk)
        )

    def like(self) -> None:
        """
        Like post

        :return: none
        """
        client.post_like(self.pk)

    def unlike(self) -> None:
        """
        Unlike post

        :return: none
        """
        client.delete_like(self.pk)


__all__ = [
    "Feed",
]
