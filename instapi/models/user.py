from collections import Counter as RealCounter
from itertools import chain
from typing import (
    Any,
    Counter,
    Dict,
    Iterable,
    List,
    Optional,
    TYPE_CHECKING,
)

from dataclasses import (
    dataclass,
)

from instapi.client import client
from instapi.models.base import Entity
from instapi.models.resource import Resource
from instapi.utils import (
    fetcher,
    process_many,
)

if TYPE_CHECKING:
    from instapi.models.feed import Feed


@dataclass(frozen=True)
class User(Entity):
    username: str
    full_name: str
    is_private: bool
    is_verified: bool

    @classmethod
    def get(cls, pk: int) -> 'User':
        return cls.__from_dict__(client.user_info(pk)['user'])

    @classmethod
    def from_username(cls, username: str) -> 'User':
        return cls.__from_dict__(client.username_info(username)['user'])

    @classmethod
    def self(cls) -> 'User':
        return cls.get(client.current_user()['user']['pk'])

    @property
    def biography(self) -> int:
        return self.user_detail()['biography']

    @property
    def media_count(self) -> int:
        return self.user_detail()['media_count']

    @property
    def follower_count(self) -> int:
        return self.user_detail()['follower_count']

    @property
    def following_count(self) -> int:
        return self.user_detail()['following_count']

    def user_detail(self) -> Dict[str, Any]:
        return self.full_info()['user_detail']['user']

    def full_info(self) -> Dict[str, Any]:
        return client.user_detail_info(self.pk)

    def follow(self, user: 'User'):
        if self != User.self():
            raise ValueError()

        client.friendships_create(user.pk)

    def unfollow(self, user: 'User'):
        if self != User.self():
            raise ValueError()

        client.friendships_destroy(user.pk)

    def iter_images(self) -> Iterable['Resource']:
        for feed in self.iter_feeds():
            yield from feed.images()

    @fetcher(iter_images)
    def images(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    def iter_videos(self) -> Iterable['Resource']:
        for feed in self.feeds():
            yield from feed.videos()

    @fetcher(iter_videos)
    def videos(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    def iter_resources(self) -> Iterable['Resource']:
        for feed in self.iter_feeds():
            yield from feed.iter_resources()

    @fetcher(iter_resources)
    def resources(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    def iter_followers(self) -> Iterable['User']:
        for result in process_many(client.user_followers, self.pk, with_rank_token=True):
            yield from map(User.__from_dict__, result['users'])

    @fetcher(iter_followers)
    def followers(self, limit: Optional[int] = None) -> List['User']:
        ...

    def iter_followings(self) -> Iterable['User']:
        for result in process_many(client.user_following, self.pk, with_rank_token=True):
            yield from map(User.__from_dict__, result['users'])

    @fetcher(iter_followings)
    def followings(self, ) -> List['User']:
        ...

    def iter_feeds(self) -> Iterable['Feed']:
        from instapi.models.feed import Feed
        for result in process_many(client.user_feed, self.pk):
            yield from map(Feed.__from_dict__, result['items'])

    @fetcher(iter_feeds)
    def feeds(self, limit: Optional[int] = None) -> List['Feed']:
        ...

    def total_comments(self) -> int:
        return sum(feed.comment_count for feed in self.iter_feeds())

    def total_likes(self) -> int:
        return sum(feed.like_count for feed in self.iter_feeds())

    def likes_chain(self) -> Iterable['User']:
        return chain.from_iterable(feed.iter_likes() for feed in self.iter_feeds())

    def likes_statistic(self) -> Counter['User']:
        return RealCounter(self.likes_chain())

    def liked_by_user(self, user: 'User') -> List['Feed']:
        return [f for f in self.iter_feeds() if f.liked_by(user)]


__all__ = [
    'User',
]
