from collections import Counter
from typing import (
    Iterable,
    List,
    Tuple,
)

from pytest import (
    fixture,
    raises,
)

from instapi.client import client
from instapi.models import (
    Feed,
    User,
)
from instapi.models.resource import (
    Image,
    Resources,
    Video,
)
from instapi.utils import flat
from .conftest import (
    create_feeds,
    create_images,
    create_users,
    create_videos,
)
from ..conftest import (
    random_int,
    random_string,
)


@fixture()
def mock_feeds_with_resources(mocker) -> Tuple[List[Feed], List[Image], List[Video]]:
    """
    Fixture that mocks user feeds and feeds resources
    """
    mocker.patch('instapi.models.User.iter_feeds')
    mocker.patch('instapi.models.Feed.iter_images')
    mocker.patch('instapi.models.Feed.iter_videos')
    mocker.patch('instapi.models.Feed.iter_resources')

    feeds = create_feeds()
    images = create_images(length=1)
    videos = create_videos(length=1)

    User.iter_feeds.return_value = feeds

    def mocked_resources(video: bool = True, image: bool = True) -> Iterable[Resources]:
        if video:
            yield from videos
        if image:
            yield from images

    Feed.iter_images.return_value = images
    Feed.iter_videos.return_value = videos
    Feed.iter_resources.side_effect = mocked_resources

    return feeds, images, videos


@fixture()
def mock_feeds(mocker) -> List[Feed]:
    """
    Fixture that mocks user feeds
    """
    feeds = create_feeds()
    mocker.patch('instapi.client.client.user_feed', return_value={'items': [*map(vars, feeds)]})

    return feeds


def test_user_get(user, mocker):
    """Test for User.get classmethod"""
    mocker.patch('instapi.client.client.user_info', return_value={'user': vars(user)})

    assert User.get(user.pk) == user
    client.user_info.assert_called_once_with(user.pk)


def test_user_from_username(user, mocker):
    """Test for User.from_username classmethod"""
    mocker.patch('instapi.client.client.username_info', return_value={'user': vars(user)})

    assert User.from_username(user.username) == user
    client.username_info.assert_called_once_with(user.username)


def test_user_match_username(user, mocker):
    """Test for User.match_username classmethod"""
    list_of_users = create_users(length=50)

    mocker.patch('instapi.client.client.search_users', return_value={'users': [*map(vars, list_of_users)]})

    assert User.match_username(user.username) == list_of_users
    client.search_users.assert_called_once_with(query=user.username)

    client.search_users.reset_mock()

    limit = 10
    client.search_users.return_value = {'users': [*map(vars, list_of_users[:limit])]}

    assert User.match_username(user.username, limit=limit) == list_of_users[:limit]
    client.search_users.assert_called_once_with(query=user.username, count=limit)


def test_user_self(user, mocker):
    """Test for User.self classmethod"""
    mocker.patch('instapi.client.client.user_info', return_value={'user': vars(user)})
    mocker.patch('instapi.client.client.current_user', return_value={'user': vars(user)})

    assert User.self() == user
    client.current_user.assert_called_once_with()
    client.user_info.assert_called_once_with(user.pk)


def test_user_details(user, mocker):
    """
    Test for:
    User.biography property
    User.media_count property
    User.follower_count property
    User.following_count property
    User.user_detail method
    User.full_info method
    """
    user_details = {
        'biography': random_string(),
        'media_count': random_int(),
        'follower_count': random_int(),
        'following_count': random_int(),
        **vars(user),
    }
    full_info = {'user_detail': {'user': user_details}}

    mocker.patch('instapi.client.client.user_detail_info', return_value=full_info)

    assert user.biography == user_details['biography']
    assert user.media_count == user_details['media_count']
    assert user.follower_count == user_details['follower_count']
    assert user.following_count == user_details['following_count']
    assert user.user_detail() == user_details
    assert user.full_info() == full_info

    client.user_detail_info.assert_called_with(user.pk)
    assert client.user_detail_info.call_count == 6


def test_follow(user, mocker):
    """Test for User.follow method"""
    self, = create_users(length=1)

    mocker.patch('instapi.client.client.friendships_create')
    mocker.patch('instapi.models.User.self', return_value=self)

    with raises(ValueError):
        user.follow(self)

    client.friendships_create.assert_not_called()

    self.follow(user)

    client.friendships_create.assert_called_once_with(user.pk)


def test_unfollow(user, mocker):
    """Test for User.unfollow method"""
    self, = create_users(length=1)

    mocker.patch('instapi.client.client.friendships_destroy')
    mocker.patch('instapi.models.User.self', return_value=self)

    with raises(ValueError):
        user.unfollow(self)

    client.friendships_destroy.assert_not_called()

    self.unfollow(user)

    client.friendships_destroy.assert_called_once_with(user.pk)


def test_images(user, mock_feeds_with_resources):
    """
    Test for:
    User.iter_images method
    User.images method
    """
    feeds, images, _ = mock_feeds_with_resources

    expected = flat([images] * len(feeds))

    assert [*user.iter_images()] == expected
    assert Feed.iter_images.call_count == len(feeds)

    Feed.iter_images.reset_mock()

    assert user.images() == expected
    assert Feed.iter_images.call_count == len(feeds)

    Feed.iter_images.reset_mock()

    limit = len(expected) - len(expected) // 2

    assert user.images(limit=limit) == expected[:limit]
    assert Feed.iter_images.call_count == limit


def test_videos(user, mock_feeds_with_resources):
    """
    Test for:
    User.iter_videos method
    User.videos method
    """
    feeds, _, videos = mock_feeds_with_resources

    expected = flat([videos] * len(feeds))

    assert [*user.iter_videos()] == expected
    assert Feed.iter_videos.call_count == len(feeds)

    Feed.iter_videos.reset_mock()

    assert user.videos() == expected
    assert Feed.iter_videos.call_count == len(feeds)

    Feed.iter_videos.reset_mock()

    limit = len(expected) - len(expected) // 2

    assert user.videos(limit=limit) == expected[:limit]
    assert Feed.iter_videos.call_count == limit


def test_resources(user, mock_feeds_with_resources):
    """
    Test for:
    User.iter_resources method
    User.resources method
    """
    feeds, images, videos = mock_feeds_with_resources

    expected = flat([videos, images] * len(feeds))

    assert [*user.iter_resources()] == expected
    assert Feed.iter_resources.call_count == len(feeds)

    Feed.iter_resources.reset_mock()

    assert user.resources() == expected
    assert Feed.iter_resources.call_count == len(feeds)

    Feed.iter_videos.reset_mock()

    limit = len(expected) - len(expected) // 2
    assert user.resources(limit=limit) == expected[:limit]


def test_followers(user, mocker):
    """
    Test for:
    User.iter_followers method
    User.followers method
    """
    users = create_users()
    mocker.patch('instapi.client.client.user_followers', return_value={'users': [*map(vars, users)]})

    assert [*user.iter_followers()] == users
    client.user_followers.assert_called_once()
    assert client.user_followers.call_args[0][0] == user.pk

    client.user_followers.reset_mock()

    assert user.followers() == users
    client.user_followers.assert_called_once()
    assert client.user_followers.call_args[0][0] == user.pk

    client.user_followers.reset_mock()

    limit = len(users) - len(users) // 2
    assert user.followers(limit=limit) == users[:limit]


def test_followings(user, mocker):
    """
    Test for:
    User.iter_followings method
    User.followings method
    """
    users = create_users()
    mocker.patch('instapi.client.client.user_following', return_value={'users': [*map(vars, users)]})

    assert [*user.iter_followings()] == users
    client.user_following.assert_called_once()
    assert client.user_following.call_args[0][0] == user.pk

    client.user_following.reset_mock()

    assert user.followings() == users
    client.user_following.assert_called_once()
    assert client.user_following.call_args[0][0] == user.pk

    client.user_following.reset_mock()

    limit = len(users) - len(users) // 2
    assert user.followings(limit=limit) == users[:limit]


def test_feeds(user, mock_feeds):
    """
    Test for:
    User.iter_feeds
    User.feeds
    """
    assert [*user.iter_feeds()] == mock_feeds
    client.user_feed.assert_called_once_with(user.pk)

    client.user_feed.reset_mock()

    assert user.feeds() == mock_feeds
    client.user_feed.assert_called_once_with(user.pk)

    client.user_feed.reset_mock()

    limit = len(mock_feeds) - len(mock_feeds) // 2
    assert user.feeds(limit=limit) == mock_feeds[:limit]


def test_total_comments_and_likes(user, mock_feeds):
    """
    Test for:
    User.total_comments
    User.total_likes
    """
    likes = sum(f.like_count for f in mock_feeds)
    assert user.total_likes() == likes

    comments = sum(f.comment_count for f in mock_feeds)
    assert user.total_comments() == comments


def test_likes(user, mock_feeds, mocker):
    """
    Test for:
    User.likes_chain
    User.likes_statistic
    """
    users = create_users()
    mocker.patch('instapi.models.Feed.iter_likes', return_value=users)

    expected = flat([users] * len(mock_feeds))

    assert [*user.likes_chain()] == expected
    client.user_feed.assert_called_once_with(user.pk)

    client.user_feed.reset_mock()

    assert user.likes_statistic() == Counter(expected)
    client.user_feed.assert_called_once_with(user.pk)


def test_liked_by(user, mock_feeds, mocker):
    """
    Test for:
    User.iter_liked_by_user
    User.liked_by_user
    """
    users = create_users()
    mocker.patch('instapi.models.Feed.liked_by')

    def assert_method(like_user: User, expected: List[Feed]):
        Feed.liked_by.reset_mock()
        assert [*user.iter_liked_by_user(like_user)] == expected
        assert Feed.liked_by.call_count == len(users)

        Feed.liked_by.reset_mock()
        assert user.liked_by_user(like_user) == expected
        assert Feed.liked_by.call_count == len(users)

    for u in users:
        # Looks complicated, list contains cycle to mark first feed
        # as liked twice for iter_liked_by_user and liked_by_user
        Feed.liked_by.side_effect = ([True] + [False] * (len(mock_feeds) - 1)) * 2
        assert_method(u, [mock_feeds[0]])

    def _liked_by_all_liked(user: User) -> bool:
        return u == user

    Feed.liked_by.side_effect = _liked_by_all_liked

    for u in users:
        assert_method(u, mock_feeds)

    Feed.liked_by.side_effect = None
    Feed.liked_by.return_value = False

    for u in users:
        assert_method(u, [])


def test_stories(user, mocker):
    """
    Test for:
    User.iter_stories
    User.stories
    """
    images = create_images()
    videos = create_videos()

    expected = [*videos, *images]

    return_value = {'reel': {'items': flat([
        [{'video_versions': [vars(v)]} for v in videos],
        [{'image_versions2': {'candidates': [vars(i)]}} for i in images],
    ])}}

    mocker.patch('instapi.client.client.user_story_feed', return_value=return_value)

    assert [*user.iter_stories()] == expected
    client.user_story_feed.assert_called_once_with(user.pk)

    client.user_story_feed.reset_mock()

    assert user.stories() == expected
    client.user_story_feed.assert_called_once_with(user.pk)

    client.user_story_feed.reset_mock()

    limit = len(expected) - len(expected) // 2

    assert user.stories(limit=limit) == expected[:limit]
    client.user_story_feed.assert_called_once_with(user.pk)
