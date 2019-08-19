from collections import Counter as RealCounter
from itertools import chain
from typing import (
    Any,
    Counter,
    Dict,
    Iterable,
    List,
    Set,
)

from dataclasses import (
    dataclass,
    field,
    fields,
)

from instapi.client import client
from instapi.utils import process_many


@dataclass(frozen=True)
class BaseModel:
    @classmethod
    def __field_names__(cls):
        return {f.name for f in fields(cls)}

    @classmethod
    def __from_dict__(cls, data: Dict[str, Any]):
        return cls(**{k: data[k] for k in cls.__field_names__()})


@dataclass(frozen=True)
class Entity(BaseModel):
    pk: int = field(repr=False)


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

    def full_info(self) -> Dict[str, Any]:
        return client.user_detail_info(self.pk)

    def user_detail(self) -> Dict[str, Any]:
        return self.full_info()['user_detail']['user']

    def follow(self, user: 'User'):
        if self != User.self():
            raise ValueError()

        client.friendships_create(user.pk)

    def unfollow(self, user: 'User'):
        if self != User.self():
            raise ValueError()

        client.friendships_destroy(user.pk)

    def iter_followers(self) -> Iterable['User']:
        for result in process_many(client.user_followers, self.pk, with_rank_token=True):
            yield from map(User.__from_dict__, result['users'])

    def followers(self) -> Set['User']:
        return {*self.iter_followers()}

    def iter_followings(self) -> Iterable['User']:
        for result in process_many(client.user_following, self.pk, with_rank_token=True):
            yield from map(User.__from_dict__, result['users'])

    def followings(self) -> Set['User']:
        return {*self.iter_followings()}

    def iter_feeds(self) -> Iterable['Feed']:
        for result in process_many(client.user_feed, self.pk):
            yield from map(Feed.__from_dict__, result['items'])

    def feeds(self) -> Set['Feed']:
        return {*self.iter_feeds()}

    def total_likes(self) -> int:
        return sum(feed.like_count for feed in self.iter_feeds())

    def likes_chain(self) -> Iterable['User']:
        return chain.from_iterable(feed.iter_likes() for feed in self.iter_feeds())

    def likes_statistic(self) -> Counter['User']:
        return RealCounter(self.likes_chain())

    def likes_by_user(self, user: 'User') -> List['Feed']:
        return [f for f in self.feeds() if f.liked_by(user)]

    def total_comments(self) -> int:
        return sum(feed.comment_count for feed in self.iter_feeds())


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> Dict[str, Any]:
        items, *_ = client.media_info(self.pk)['items']
        return items


@dataclass(frozen=True)
class Feed(Media):
    like_count: int
    comment_count: int

    def iter_likes(self) -> Iterable['User']:
        for result in process_many(client.media_likers, self.pk):
            yield from map(User.__from_dict__, result['users'])

    def likes(self) -> Set['User']:
        return {*self.iter_likes()}

    def iter_comments(self) -> Iterable['Comment']:
        for result in process_many(client.media_comments, self.pk):
            for c in result['comments']:
                c['user'] = User.__from_dict__(c['user'])

            yield from map(Comment.__from_dict__, result['comments'])

    def liked_by(self, user: 'User') -> bool:
        for result in process_many(client.media_likers, self.pk):
            if user.pk in result['users']:
                return True
        else:
            return False

    def comments(self) -> Set['Comment']:
        return {*self.iter_comments()}


@dataclass(frozen=True)
class Comment(Media):
    text: str
    user: User
