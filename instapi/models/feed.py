from typing import (
    Iterable,
    List,
    Optional,
)

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import Media
from instapi.models.comment import Comment
from instapi.models.resource import (
    Image,
    Resources,
    Video,
)
from instapi.models.user import User
from instapi.utils import (
    process_many,
    to_list,
)


@dataclass(frozen=True)
class Feed(Media):
    like_count: int
    comment_count: int

    @classmethod
    def iter_timeline(cls) -> Iterable['Feed']:
        for result in process_many(client.feed_timeline):
            yield from (
                Feed.create(data['media_or_ad']) for data in result['feed_items']
                if 'media_or_ad' in data
            )

    @classmethod
    def timeline(cls, limit: Optional[int] = None) -> List['Feed']:
        return to_list(cls.iter_timeline(), limit=limit)

    def iter_likes(self) -> Iterable['User']:
        for result in process_many(client.media_likers, self.pk):
            yield from map(User.create, result['users'])

    def likes(self, limit: Optional[int] = None) -> List['User']:
        return to_list(self.iter_likes(), limit=limit)

    def liked_by(self, user: 'User') -> bool:
        return any(
            any(user.pk == u['pk'] for u in result['users'])
            for result in process_many(client.media_likers, self.pk)
        )

    def like(self) -> None:
        client.post_like(self.pk)

    def unlike(self) -> None:
        client.delete_like(self.pk)

    def iter_comments(self) -> Iterable['Comment']:
        for result in process_many(client.media_comments, self.pk):
            for c in result['comments']:
                c['user'] = User.create(c['user'])

            yield from map(Comment.create, result['comments'])

    def comments(self, limit: Optional[int] = None) -> List['Comment']:
        return to_list(self.iter_comments(), limit=limit)

    def iter_resources(self, *, video: bool = True, image: bool = True) -> Iterable[Resources]:
        # TODO: implement ability to fetch media with different quality
        media_info = self._media_info()
        carousel_media = media_info.get('carousel_media', [media_info])

        for media in carousel_media:
            if 'video_versions' in media and video:
                yield Video.create(media['video_versions'][0])
            elif 'video_versions' not in media and image:
                yield Image.create(media['image_versions2']['candidates'][0])

    def resources(self, video: bool = True, image: bool = True, limit: Optional[int] = None) -> List[Resources]:
        return to_list(self.iter_resources(video=video, image=image), limit=limit)

    def iter_videos(self) -> Iterable['Video']:
        return self.iter_resources(video=True, image=False)

    def videos(self, limit: Optional[int] = None) -> List['Video']:
        return to_list(self.iter_videos(), limit=limit)

    def iter_images(self) -> Iterable['Image']:
        return self.iter_resources(video=False, image=True)

    def images(self, limit: Optional[int] = None) -> List['Image']:
        return to_list(self.iter_images(), limit=limit)

    def image(self) -> Optional['Image']:
        return next(iter(self.iter_images()), None)

    def video(self) -> Optional['Video']:
        return next(iter(self.iter_videos()), None)


__all__ = [
    'Feed',
]
