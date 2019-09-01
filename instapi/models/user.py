from collections import Counter as RealCounter
from itertools import chain
from typing import (
    Any,
    cast,
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
from instapi.models.resource import (
    Image,
    Resource,
    Resources,
    Video,
)
from instapi.utils import (
    process_many,
    to_list,
)

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
        return cls.create(client.user_info(pk)['user'])

    @classmethod
    def from_username(cls, username: str) -> 'User':
        return cls.create(client.username_info(username)['user'])

    @classmethod
    def match_username(cls, username: str, limit: Optional[int] = None) -> List['User']:
        response = client.search_users(
            query=username,
            **({'count': limit} if limit is not None else {}),
        )

        return [cls.create(user) for user in response['users']]

    @classmethod
    def self(cls) -> 'User':
        return cls.get(client.current_user()['user']['pk'])

    @property
    def biography(self) -> str:
        return cast(str, self.user_detail()['biography'])

    @property
    def media_count(self) -> int:
        return cast(int, self.user_detail()['media_count'])

    @property
    def follower_count(self) -> int:
        return cast(int, self.user_detail()['follower_count'])

    @property
    def following_count(self) -> int:
        return cast(int, self.user_detail()['following_count'])

    def user_detail(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], self.full_info()['user_detail']['user'])

    def full_info(self) -> Dict[str, Any]:
        return cast(Dict[str, Any], client.user_detail_info(self.pk))

    def follow(self, user: 'User') -> None:
        if self != User.self():
            raise ValueError()

        client.friendships_create(user.pk)

    def unfollow(self, user: 'User') -> None:
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
        for result in process_many(client.user_following, self.pk, with_rank_token=True):
            yield from map(User.create, result['users'])

    def followings(self, limit: Optional[int] = None) -> List['User']:
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
        for result in (client.user_story_feed(self.pk)['reel'] or {}).get('items', ()):
            if 'video_versions' in result:
                yield Video.create(result['video_versions'][0])
            else:
                yield Image.create(result['image_versions2']['candidates'][0])

    def stories(self, limit: Optional[int] = None) -> List['Resources']:
        return to_list(self.iter_stories(), limit=limit)


__all__ = [
    'User',
]
