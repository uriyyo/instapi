from functools import partial
from typing import (
    Iterable,
    List,
    Optional,
)

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Media
from instapi.models.comment import Comment
from instapi.models.resource import Resource
from instapi.models.user import User
from instapi.utils import (
    fetcher,
    process_many,
)


@dataclass(frozen=True)
class Feed(Media):
    like_count: int
    comment_count: int

    @classmethod
    def iter_timeline(cls) -> Iterable['Feed']:
        for result in process_many(client.feed_timeline):
            yield from (
                Feed.__from_dict__(data['media_or_ad']) for data in result['feed_items']
                if 'media_or_ad' in data
            )

    @classmethod
    @fetcher(iter_timeline)
    def timeline(cls, limit: Optional[int] = None) -> List['Feed']:
        ...

    def iter_likes(self) -> Iterable['User']:
        for result in process_many(client.media_likers, self.pk):
            yield from map(User.__from_dict__, result['users'])

    @fetcher(iter_likes)
    def likes(self, limit: Optional[int] = None) -> List['User']:
        ...

    def liked_by(self, user: 'User') -> bool:
        return any(
            user.pk in result['users'] for result
            in process_many(client.media_likers, self.pk)
        )

    def like(self) -> None:
        client.post_like(self.pk)

    def unlike(self) -> None:
        client.delete_like(self.pk)

    def iter_comments(self) -> Iterable['Comment']:
        for result in process_many(client.media_comments, self.pk):
            for c in result['comments']:
                c['user'] = User.__from_dict__(c['user'])

            yield from map(Comment.__from_dict__, result['comments'])

    @fetcher(iter_comments)
    def comments(self, limit: Optional[int] = None) -> List['Comment']:
        ...

    def iter_resources(self, *, video: bool = True, image: bool = True) -> Iterable['Resource']:
        media_info = self._media_info()
        carousel_media = media_info.get('carousel_media', [media_info])

        for media in carousel_media:
            if 'video_versions' in media and video:
                yield Resource.__from_dict__(media['video_versions'][0])
            elif 'video_versions' not in media and image:
                yield Resource.__from_dict__(media['image_versions2']['candidates'][0])

    @fetcher(iter_resources)
    def resources(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    @fetcher(partial(iter_resources, video=True, image=False))
    def videos(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    @fetcher(partial(iter_resources, video=False, image=True))
    def images(self, limit: Optional[int] = None) -> List['Resource']:
        ...

    def image(self) -> Optional['Resource']:
        try:
            return self.images()[0]
        except IndexError:
            return None

    def video(self) -> Optional['Resource']:
        try:
            return self.videos()[0]
        except IndexError:
            return None


__all__ = [
    'Feed',
]
