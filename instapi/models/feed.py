from typing import (
    cast,
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
    """
    This class represent Instagram's feed. It gives opportunity to:
    -   Get posts from feed
    -   Get info about post (comments, which was attached to the post; users, which has liked the post)
    -   Like/Unlike posts
    -   Get media (videos and images) from posts
    """
    like_count: int
    comment_count: int

    @classmethod
    def iter_timeline(cls) -> Iterable['Feed']:
        """
        Create generator for iteration over posts from feed

        :return: generator with posts from feed
        """
        for result in process_many(client.feed_timeline):
            yield from (
                Feed.create(data['media_or_ad']) for data in result['feed_items']
                if 'media_or_ad' in data
            )

    @classmethod
    def timeline(cls, limit: Optional[int] = None) -> List['Feed']:
        """
        Generate list of posts from feed

        :param limit: number of posts, which will be added to the list
        :return: list with posts from feed
        """
        return to_list(cls.iter_timeline(), limit=limit)

    def iter_likes(self) -> Iterable['User']:
        """
        Create generator for iteration over posts from feed

        :return: generator with users, which has liked a post
        """
        for result in process_many(client.media_likers, self.pk):
            yield from map(User.create, result['users'])

    def likes(self, limit: Optional[int] = None) -> List['User']:
        """
        Generate list of users, which has liked a post

        :param limit: number of users, which will be added to the list
        :return: list with users, which has liked a post
        """
        return to_list(self.iter_likes(), limit=limit)

    def liked_by(self, user: 'User') -> bool:
        """
        Check if post was liked by user

        :param user: user for checking
        :return: boolean value
        """
        return any(
            any(user.pk == u['pk'] for u in result['users'])
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

    def iter_comments(self) -> Iterable['Comment']:
        """
        Create generator for iteration over comments, which was attached to the post

        :return: generator with comments
        """
        for result in process_many(client.media_comments, self.pk):
            for c in result['comments']:
                c['user'] = User.create(c['user'])

            yield from map(Comment.create, result['comments'])

    def comments(self, limit: Optional[int] = None) -> List['Comment']:
        """
        Generate list of comments, which was attached to the post

        :param limit: number of comments, which will be added to the list
        :return: list with comments
        """
        return to_list(self.iter_comments(), limit=limit)

    def iter_resources(self, *, video: bool = True, image: bool = True) -> Iterable[Resources]:
        """
        Create generator for iteration over images/videos, which contains in the post

        :param video: true - add videos, false - ignore videos
        :param image: true - add images, false - ignore images
        :return: generator with images/videos
        """
        # TODO: implement ability to fetch media with different quality
        media_info = self._media_info()
        carousel_media = media_info.get('carousel_media', [media_info])

        for media in carousel_media:
            if 'video_versions' in media and video:
                yield Video.create(media['video_versions'][0])
            elif 'video_versions' not in media and image:
                yield Image.create(media['image_versions2']['candidates'][0])

    def resources(self, video: bool = True, image: bool = True, limit: Optional[int] = None) -> List[Resources]:
        """
        Generate list of images/videos, which contains in the post

        :param video: true - add videos, false - ignore videos
        :param image: true - add images, false - ignore images
        :param limit: number of images/videos, which will be added to the list
        :return: list with images/videos
        """
        return to_list(self.iter_resources(video=video, image=image), limit=limit)

    def iter_videos(self) -> Iterable['Video']:
        """
        Create generator for iteration over videos, which contains in the post

        :return: generator with videos, which contains in the post
        """
        return cast(Iterable['Video'], self.iter_resources(video=True, image=False))

    def videos(self, limit: Optional[int] = None) -> List['Video']:
        """
        Generate list of videos, which contains in the post

        :param limit: number of videos, which will be added to the list
        :return: list with videos
        """
        return to_list(self.iter_videos(), limit=limit)

    def iter_images(self) -> Iterable['Image']:
        """
        Create generator for iteration over images, which contains in the post

        :return: generator with image, which contains in the post
        """
        return cast(Iterable['Image'], self.iter_resources(video=False, image=True))

    def images(self, limit: Optional[int] = None) -> List['Image']:
        """
        Generate list of images, which contains in the post

        :param limit: number of images, which will be added to the list
        :return: list with images
        """
        return to_list(self.iter_images(), limit=limit)

    def image(self) -> Optional['Image']:
        """
        Return the first image from feed if it exists.

        :return: image or None
        """
        return next(iter(self.iter_images()), None)

    def video(self) -> Optional['Video']:
        """
        Return the first video from feed if it exists

        :return: video or None
        """
        return next(iter(self.iter_videos()), None)


__all__ = [
    'Feed',
]
