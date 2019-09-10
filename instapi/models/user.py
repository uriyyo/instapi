from collections import Counter as RealCounter
from itertools import chain
from typing import TYPE_CHECKING
from typing import Counter
from typing import Iterable
from typing import List
from typing import Optional
from typing import cast

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Entity
from instapi.models.resource import Resource
from instapi.models.resource import Resources
from instapi.types import StrDict
from instapi.utils import process_many
from instapi.utils import to_list

if TYPE_CHECKING:
    from instapi.models.feed import Feed  # pragma: no cover


@dataclass(frozen=True)
class User(Entity):
    username: str
    full_name: str
    is_private: bool
    is_verified: bool

    @classmethod
    def get(cls, pk: int) -> 'User':
        """
        Create User object from unique user's identifier

        :param pk: unique user's identifier
        :return: User object
        """
        return cls.create(client.user_info(pk)['user'])

    @classmethod
    def from_username(cls, username: str) -> 'User':
        """
        Create User object from username

        :param username: name of user
        :return: User object
        """
        return cls.create(client.username_info(username)['user'])

    @classmethod
    def match_username(cls, username: str, limit: Optional[int] = None) -> List['User']:
        """
        Search users by username

        :param username: username
        :param limit: size of resulting list
        :return: list of User objects
        """
        response = client.search_users(
            query=username,
            **({'count': limit} if limit is not None else {}),
        )

        return [cls.create(user) for user in response['users']]

    @classmethod
    def self(cls) -> 'User':
        """
        Create User object from current user

        :return: User object
        """
        return cls.get(client.current_user()['user']['pk'])

    @property
    def biography(self) -> str:
        """
        Return biography of user

        :return: string
        """
        return cast(str, self.user_detail()['biography'])

    @property
    def media_count(self) -> int:
        """
        Return user's count of post

        :return: number
        """
        return cast(int, self.user_detail()['media_count'])

    @property
    def follower_count(self) -> int:
        """
        Return user's count of followers

        :return: number
        """
        return cast(int, self.user_detail()['follower_count'])

    @property
    def following_count(self) -> int:
        """
        Return count of people, on which user followed

        :return: number
        """
        return cast(int, self.user_detail()['following_count'])

    def user_detail(self) -> StrDict:
        return cast(StrDict, self.full_info()['user_detail']['user'])

    def full_info(self) -> StrDict:
        return cast(StrDict, client.user_detail_info(self.pk))

    def follow(self, user: 'User') -> None:
        """
        Follow on user

        :param user: User object
        :return: None
        """
        if self != User.self():
            raise ValueError()

        client.friendships_create(user.pk)

    def unfollow(self, user: 'User') -> None:
        """
        Unfollow from user

        :param user: User object
        :return: None
        """
        if self != User.self():
            raise ValueError()

        client.friendships_destroy(user.pk)

    def iter_images(self) -> Iterable['Resource']:
        for feed in self.iter_feeds():
            yield from feed.images()

    def images(self, limit: Optional[int] = None) -> List['Resource']:
        return to_list(self.iter_images(), limit=limit)

    def iter_videos(self) -> Iterable['Resource']:
        for feed in self.feeds():
            yield from feed.videos()

    def videos(self, limit: Optional[int] = None) -> List['Resource']:
        return to_list(self.iter_videos(), limit=limit)

    def iter_resources(self) -> Iterable['Resource']:
        for feed in self.iter_feeds():
            yield from feed.iter_resources()

    def resources(self, limit: Optional[int] = None) -> List['Resource']:
        return to_list(self.iter_resources(), limit=limit)

    def iter_followers(self) -> Iterable['User']:
        for result in process_many(client.user_followers, self.pk, with_rank_token=True):
            yield from map(User.create, result['users'])

    def followers(self, limit: Optional[int] = None) -> List['User']:
        return to_list(self.iter_followers(), limit=limit)

    def iter_followings(self) -> Iterable['User']:
        """
        Create generator for followers

        :return: generator with User objects
        """
        for result in process_many(client.user_following, self.pk, with_rank_token=True):
            yield from map(User.create, result['users'])

    def followings(self, limit: Optional[int] = None) -> List['User']:
        """
        Generate list of followers

        :param limit: number of images, which will be added to the list
        :return: list with User objects
        """
        return to_list(self.iter_followings(), limit=limit)

    def iter_feeds(self) -> Iterable['Feed']:
        from instapi.models.feed import Feed
        for result in process_many(client.user_feed, self.pk):
            yield from map(Feed.create, result['items'])

    def feeds(self, limit: Optional[int] = None) -> List['Feed']:
        return to_list(self.iter_feeds(), limit=limit)

    def total_comments(self) -> int:
        return sum(feed.comment_count for feed in self.iter_feeds())

    def total_likes(self) -> int:
        return sum(feed.like_count for feed in self.iter_feeds())

    def likes_chain(self) -> Iterable['User']:
        return chain.from_iterable(feed.iter_likes() for feed in self.iter_feeds())

    def likes_statistic(self) -> Counter['User']:
        return RealCounter(self.likes_chain())

    def iter_liked_by_user(self, user: 'User') -> Iterable['Feed']:
        return (f for f in self.iter_feeds() if f.liked_by(user))

    def liked_by_user(self, user: 'User', limit: Optional[int] = None) -> List['Feed']:
        return to_list(self.iter_liked_by_user(user), limit=limit)

    def iter_stories(self) -> Iterable['Resources']:
        items = (client.user_story_feed(self.pk)['reel'] or {}).get('items', ())
        return Resource.create_resources(items)

    def stories(self, limit: Optional[int] = None) -> List['Resources']:
        return to_list(self.iter_stories(), limit=limit)


__all__ = [
    'User',
]
