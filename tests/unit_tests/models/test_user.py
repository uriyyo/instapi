from collections import Counter
from typing import (
    Iterable,
    List,
)

from pytest import (
    fixture,
    raises,
)

from instapi.models import (
    Feed,
    User,
)
from instapi.models.resource import (
    Resources,
)
from instapi.utils import flat
from .conftest import (
    as_dicts,
    create_users,
)
from ..conftest import (
    random_int,
    random_string,
)


@fixture()
def mock_feeds_with_resources(mocker, feeds, images, videos):
    """
    Fixture that mocks user feeds and feeds resources
    """
    mocker.patch('instapi.models.User.iter_feeds', return_value=feeds)
    mocker.patch('instapi.models.Media._media_info', return_value={})

    def mocked_resources(resource_data, video: bool = True, image: bool = True) -> Iterable[Resources]:
        if video:
            yield from videos
        if image:
            yield from images

    mocker.patch('instapi.Resource.create_resources', side_effect=mocked_resources)


@fixture()
def mock_feeds(mocker, feeds) -> List[Feed]:
    """
    Fixture that mocks user feeds
    """
    return mocker.patch(
        'instapi.client.client.user_feed',
        return_value={'items': as_dicts(feeds)},
    )


def test_user_get(user, mocker):
    """Test for User.get classmethod"""
    user_info_mock = mocker.patch('instapi.client.client.user_info', return_value={'user': user.as_dict()})

    assert User.get(user.pk) == user

    user_info_mock.assert_called_once_with(user.pk)


def test_user_from_username(user, mocker):
    """Test for User.from_username classmethod"""
    username_info_mock = mocker.patch('instapi.client.client.username_info', return_value={'user': user.as_dict()})

    assert User.from_username(user.username) == user

    username_info_mock.assert_called_once_with(user.username)


def test_user_match_username(user, mocker):
    """Test for User.match_username classmethod"""
    list_of_users = create_users(length=50)
    search_mock = mocker.patch('instapi.client.client.search_users', return_value={'users': as_dicts(list_of_users)})

    assert User.match_username(user.username) == list_of_users

    search_mock.assert_called_once_with(query=user.username)
    search_mock.reset_mock()

    limit = 10
    search_mock.return_value = {'users': as_dicts(list_of_users[:limit])}

    assert User.match_username(user.username, limit=limit) == list_of_users[:limit]

    search_mock.assert_called_once_with(query=user.username, count=limit)


def test_user_self(user, mocker):
    """Test for User.self classmethod"""
    user_info_mock = mocker.patch('instapi.client.client.user_info', return_value={'user': user.as_dict()})
    current_user_mock = mocker.patch('instapi.client.client.current_user', return_value={'user': user.as_dict()})

    assert User.self() == user

    current_user_mock.assert_called_once_with()
    user_info_mock.assert_called_once_with(user.pk)


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
        **user.as_dict(),
    }
    full_info = {'user_detail': {'user': user_details}}

    details_mock = mocker.patch('instapi.client.client.user_detail_info', return_value=full_info)

    assert user.biography == user_details['biography']
    assert user.media_count == user_details['media_count']
    assert user.follower_count == user_details['follower_count']
    assert user.following_count == user_details['following_count']
    assert user.user_detail() == user_details
    assert user.full_info() == full_info

    details_mock.assert_called_with(user.pk)
    assert details_mock.call_count == 6


def test_follow(user, mocker):
    """Test for User.follow method"""
    self, = create_users(length=1)

    friendships_mock = mocker.patch('instapi.client.client.friendships_create')
    mocker.patch('instapi.models.User.self', return_value=self)

    with raises(ValueError):
        user.follow(self)

    friendships_mock.assert_not_called()

    self.follow(user)

    friendships_mock.assert_called_once_with(user.pk)


def test_unfollow(user, mocker):
    """Test for User.unfollow method"""
    self, = create_users(length=1)

    friendships_mock = mocker.patch('instapi.client.client.friendships_destroy')
    mocker.patch('instapi.models.User.self', return_value=self)

    with raises(ValueError):
        user.unfollow(self)

    friendships_mock.assert_not_called()

    self.unfollow(user)

    friendships_mock.assert_called_once_with(user.pk)


def test_images(mock_feeds_with_resources, user, feeds, images):
    """
    Test for:
    User.iter_images method
    User.images method
    """

    expected = flat([images] * len(feeds))

    assert [*user.iter_images()] == expected
    assert user.images() == expected

    limit = len(expected) - len(expected) // 2
    assert user.images(limit=limit) == expected[:limit]


def test_videos(mock_feeds_with_resources, user, feeds, videos):
    """
    Test for:
    User.iter_videos method
    User.videos method
    """
    expected = flat([videos] * len(feeds))

    assert [*user.iter_videos()] == expected
    assert user.videos() == expected

    limit = len(expected) - len(expected) // 2
    assert user.videos(limit=limit) == expected[:limit]


def test_resources(mock_feeds_with_resources, user, videos, images, feeds):
    """
    Test for:
    User.iter_resources method
    User.resources method
    """
    expected = flat([videos, images] * len(feeds))

    assert [*user.iter_resources()] == expected
    assert user.resources() == expected

    limit = len(expected) - len(expected) // 2
    assert user.resources(limit=limit) == expected[:limit]


def test_followers(mocker, user, users):
    """
    Test for:
    User.iter_followers method
    User.followers method
    """
    follow_mock = mocker.patch('instapi.client.client.user_followers', return_value={'users': as_dicts(users)})

    assert [*user.iter_followers()] == users
    follow_mock.assert_called_once()
    assert follow_mock.call_args[0][0] == user.pk

    follow_mock.reset_mock()

    assert user.followers() == users
    follow_mock.assert_called_once()
    assert follow_mock.call_args[0][0] == user.pk

    follow_mock.reset_mock()

    limit = len(users) - len(users) // 2
    assert user.followers(limit=limit) == users[:limit]


def test_followings(mocker, user, users):
    """
    Test for:
    User.iter_followings method
    User.followings method
    """
    follow_mock = mocker.patch('instapi.client.client.user_following', return_value={'users': as_dicts(users)})

    assert [*user.iter_followings()] == users
    follow_mock.assert_called_once()
    assert follow_mock.call_args[0][0] == user.pk

    follow_mock.reset_mock()

    assert user.followings() == users
    follow_mock.assert_called_once()
    assert follow_mock.call_args[0][0] == user.pk

    follow_mock.reset_mock()

    limit = len(users) - len(users) // 2
    assert user.followings(limit=limit) == users[:limit]


def test_feeds(mock_feeds, user, feeds):
    """
    Test for:
    User.iter_feeds
    User.feeds
    """

    assert [*user.iter_feeds()] == feeds
    assert user.feeds() == feeds

    limit = len(feeds) - len(feeds) // 2
    assert user.feeds(limit=limit) == feeds[:limit]


def test_total_comments_and_likes(mock_feeds, feeds, user):
    """
    Test for:
    User.total_comments
    User.total_likes
    """
    likes = sum(f.like_count for f in feeds)
    assert user.total_likes() == likes

    comments = sum(f.comment_count for f in feeds)
    assert user.total_comments() == comments


def test_likes(mocker, mock_feeds, user, users, feeds):
    """
    Test for:
    User.likes_chain
    User.likes_statistic
    """
    mocker.patch('instapi.models.Feed.iter_likes', return_value=users)
    expected = flat([users] * len(feeds))

    assert [*user.likes_chain()] == expected
    assert user.likes_statistic() == Counter(expected)


def test_liked_by(mocker, mock_feeds, feeds, user, users):
    """
    Test for:
    User.iter_liked_by_user
    User.liked_by_user
    """
    liked_by_mock = mocker.patch('instapi.models.Feed.liked_by')

    def assert_method(like_user: User, expected: List[Feed]):
        liked_by_mock.reset_mock()

        assert [*user.iter_liked_by_user(like_user)] == expected
        assert liked_by_mock.call_count == len(users)

        liked_by_mock.reset_mock()

        assert user.liked_by_user(like_user) == expected
        assert liked_by_mock.call_count == len(users)

    for u in users:
        # Looks complicated, list contains cycle to mark first feed
        # as liked twice for iter_liked_by_user and liked_by_user
        liked_by_mock.side_effect = ([True] + [False] * (len(feeds) - 1)) * 2
        assert_method(u, [feeds[0]])

    def _liked_by_all_liked(user: User) -> bool:
        return u == user

    liked_by_mock.side_effect = _liked_by_all_liked

    for u in users:
        assert_method(u, feeds)

    liked_by_mock.side_effect = None
    liked_by_mock.return_value = False

    for u in users:
        assert_method(u, [])


def test_stories(user, mocker, images, videos):
    """
    Test for:
    User.iter_stories
    User.stories
    """
    expected = [*videos, *images]

    return_value = {'reel': {'items': flat([
        as_dicts(videos),
        as_dicts(images),
    ])}}

    story_mock = mocker.patch('instapi.client.client.user_story_feed', return_value=return_value)

    assert [*user.iter_stories()] == expected
    story_mock.assert_called_once_with(user.pk)

    story_mock.reset_mock()

    assert user.stories() == expected
    story_mock.assert_called_once_with(user.pk)

    story_mock.reset_mock()

    limit = len(expected) - len(expected) // 2

    assert user.stories(limit=limit) == expected[:limit]
    story_mock.assert_called_once_with(user.pk)
