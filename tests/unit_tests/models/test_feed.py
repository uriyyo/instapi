from instapi import (
    User,
    Comment,
)

from instapi.client import client

from .conftest import (
    create_users,
    create_comments,
    create_feeds,
    create_videos,
    create_images,
)

from ..conftest import (
    random_int,
)


class TestFeed:

    def test_like(self, mocker, feed):
        mocker.patch('instapi.client.client.post_like')

        feed.like()

        client.post_like.assert_called_once_with(feed.pk)

    def test_unlike(self, mocker, feed):
        mocker.patch('instapi.client.client.delete_like')

        feed.unlike()

        client.delete_like.assert_called_once_with(feed.pk)

    def test_liked_by_user_in_likers(self, mocker, feed):
        media_likers = {'users': [*map(vars, create_users())]}
        mocker.patch('instapi.client.client.media_likers', return_value=media_likers)
        user = media_likers['users'][0]

        assert feed.liked_by(User.create(user))

    def test_liked_by_user_not_in_likers(self, mocker, feed, user):
        media_likers = {'users': [*map(vars, create_users())]}
        mocker.patch('instapi.client.client.media_likers', return_value=media_likers)

        assert not feed.liked_by(user)

    def test_iter_likes(self, mocker, feed):
        media_likers = {'users': [*map(vars, create_users())]}
        mocker.patch('instapi.client.client.media_likers', return_value=media_likers)

        unpack = [*feed.iter_likes()]
        assert unpack == [*map(User.create, media_likers['users'])]
        assert len(unpack) == len(media_likers['users'])

    def test_likes_without_limit(self, mocker, feed):
        media_likers = {'users': [*map(vars, create_users())]}
        mocker.patch('instapi.client.client.media_likers', return_value=media_likers)

        likes = feed.likes()
        assert likes == [*map(User.create, media_likers['users'])]
        assert len(likes) == len(media_likers['users'])

    def test_likes_with_limit(self, mocker, feed):
        media_likers = {'users': [*map(vars, create_users())]}
        mocker.patch('instapi.client.client.media_likers', return_value=media_likers)

        excepted = [*map(User.create, media_likers['users'])]
        limit = random_int(0, len(excepted))
        likes = feed.likes(limit=limit)
        assert likes == excepted[:limit]
        assert len(likes) == limit

    def test_iter_comments(self, mocker, feed):
        media_comments = {'comments': [*map(vars, create_comments())]}
        mocker.patch('instapi.client.client.media_comments', return_value=media_comments)

        unpack = [*feed.iter_comments()]
        assert unpack == [*map(Comment.create, media_comments['comments'])]
        assert len(unpack) == len(media_comments['comments'])

    def test_comments_without_limit(self, mocker, feed):
        media_comments = {'comments': [*map(vars, create_comments())]}
        mocker.patch('instapi.client.client.media_comments', return_value=media_comments)

        comments = feed.comments()
        k = [*map(Comment.create, media_comments['comments'])]
        assert comments == k
        assert len(comments) == len(media_comments['comments'])

    def test_comments_with_limit(self, mocker, feed):
        media_comments = {'comments': [*map(vars, create_comments())]}
        mocker.patch('instapi.client.client.media_comments', return_value=media_comments)

        limit = random_int(0, len(media_comments['comments']))
        comments = feed.comments(limit=limit)
        excepted = [*map(Comment.create, media_comments['comments'])]

        assert comments == excepted[:limit]
        assert len(comments) == limit

    def test_iter_timeline(self, mocker, feed):
        excepted = create_feeds()
        feed_timeline = {'feed_items': [{'media_or_ad': vars(f)} for f in excepted]}
        mocker.patch('instapi.client.client.feed_timeline', return_value=feed_timeline)

        feeds = [*feed.iter_timeline()]
        assert excepted == feeds

    def test_timeline_without_limit(self, mocker, feed):
        excepted = create_feeds()
        feed_timeline = {'feed_items': [{'media_or_ad': vars(f)} for f in excepted]}
        mocker.patch('instapi.client.client.feed_timeline', return_value=feed_timeline)

        assert feed.timeline() == excepted

    def test_timeline_with_limit(self, mocker, feed):
        excepted = create_feeds()
        feed_timeline = {'feed_items': [{'media_or_ad': vars(f)} for f in excepted]}
        mocker.patch('instapi.client.client.feed_timeline', return_value=feed_timeline)

        limit = random_int(0, len(feed_timeline['feed_items']))
        feeds = feed.timeline(limit=limit)
        assert feeds == excepted[:limit]

    def test_iter_resources_videos_without_carusel(self, mocker, feed):
        video, = create_videos(length=1)
        media_info = {'video_versions': [vars(video)]}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        resources = [*feed.iter_resources()]
        assert resources == [video]

    def test_iter_resources_images_without_carusel(self, mocker, feed):
        image, = create_images(length=1)
        media_info = {'image_versions2': {'candidates': [vars(image)]}}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        resources = [*feed.iter_resources()]
        assert resources == [image]

    def test_resources_videos(self, mocker, feed):
        video, = create_videos(length=1)
        media_info = {'video_versions': [vars(video)]}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.resources() == [video]

    def test_resources_images(self, mocker, feed):
        image, = create_images(length=1)
        media_info = {'image_versions2': {'candidates': [vars(image)]}}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.resources() == [image]

    def test_iter_videos(self, mocker, feed):
        video, = create_videos(length=1)
        media_info = {'video_versions': [vars(video)]}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert [*feed.iter_videos()] == [video]

    def test_videos(self, mocker, feed):
        video, = create_videos(length=1)
        media_info = {'video_versions': [vars(video)]}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.videos() == [video]

    def test_iter_images(self, mocker, feed):
        image, = create_images(length=1)
        media_info = {'image_versions2': {'candidates': [vars(image)]}}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert [*feed.iter_images()] == [image]

    def test_images(self, mocker, feed):
        image, = create_images(length=1)
        media_info = {'image_versions2': {'candidates': [vars(image)]}}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.images() == [image]

    def test_video(self, mocker, feed):
        video, = create_videos(length=1)
        media_info = {'video_versions': [vars(video)]}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.video() == video

    def test_image(self, mocker, feed):
        image, = create_images(length=1)
        media_info = {'image_versions2': {'candidates': [vars(image)]}}
        mocker.patch('instapi.models.base.Media._media_info', return_value=media_info)

        assert feed.image() == image