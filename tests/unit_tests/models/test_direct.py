from typing import Generator

from pytest import fixture

from instapi import (
    Direct,
    User,
)
from tests.unit_tests.models.conftest import as_dicts
from ..conftest import (
    random_int,
    random_string,
)


def test_direct_create(user):
    data = {
        'thread_title': random_string(),
        'thread_type': random_string(),
        'is_group': False,
        'users': [user.as_dict()],
        'thread_id': random_int(),
    }

    direct = Direct.create(data)

    assert {**data, 'users': tuple(User.create(d) for d in data['users'])} == vars(direct)


class TestDirects:
    @fixture
    def inbox_data(self, directs):
        return {'inbox': {'threads': as_dicts(directs)}}

    @fixture
    def mock_inbox(self, mocker, inbox_data):
        return mocker.patch('instapi.client.client.direct_v2_inbox', return_value=inbox_data)

    def test_iter_direct_return_type(self):
        assert isinstance(Direct.iter_directs(), Generator)

    def test_iter_direct(self, mock_inbox, directs):
        assert [*Direct.iter_directs()] == directs

    def test_direct(self, mock_inbox, directs):
        assert Direct.directs() == directs

    def test_direct_with_limit(self, mock_inbox, directs):
        limit = len(directs) // 2
        assert Direct.directs(limit) == directs[:limit]


class TestWithUser:
    def test_with_user_thread_exists(self, mocker, direct, user):
        mocker.patch(
            'instapi.client.client.direct_v2_get_by_participants',
            return_value={'thread': direct.as_dict()},
        )
        assert Direct.with_user(user) == direct

    def test_with_user_thread_doesnt_exists(self, mocker, user):
        mocker.patch(
            'instapi.client.client.direct_v2_get_by_participants',
            return_value={},
        )

        direct = Direct.with_user(user)

        assert direct.thread_id is None
        assert direct.users == (user,)


def test_send_text(mocker, direct):
    mock = mocker.patch('instapi.client.client.direct_v2_send_text')

    text = random_string()
    direct.send_text(text)

    mock.assert_called_once_with(
        **direct._send_args,
        text=text,
    )


def test_send_link(mocker, direct):
    mock = mocker.patch('instapi.client.client.direct_v2_send_link')

    link = random_string()
    text = random_string()
    direct.send_link(link, text)

    mock.assert_called_once_with(
        **direct._send_args,
        link=link,
        text=text,
    )


def test_send_profile(mocker, direct, user):
    mock = mocker.patch('instapi.client.client.direct_v2_send_profile')

    text = random_string()
    direct.send_profile(user, text)

    mock.assert_called_once_with(
        **direct._send_args,
        profile_id=user.pk,
        text=text,
    )


def test_send_hashtag(mocker, direct, user):
    mock = mocker.patch('instapi.client.client.direct_v2_send_hashtag')

    text = random_string()
    hashtag = random_string()
    direct.send_hashtag(hashtag, text)

    mock.assert_called_once_with(
        **direct._send_args,
        hashtag=hashtag,
        text=text,
    )


def test_send_media(mocker, direct, feed):
    mock = mocker.patch('instapi.client.client.direct_v2_send_media_share')

    text = random_string()
    direct.send_media(feed, text)

    mock.assert_called_once_with(
        **direct._send_args,
        media_id=feed.pk,
        text=text,
    )
