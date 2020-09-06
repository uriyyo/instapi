from instagram_private_api import ClientError
from pytest import fixture, mark, raises
from requests import Response

from instapi.client_api.direct import DirectEndpoint

from ..conftest import random_string


@fixture
def direct_endpoint(mocker):
    mocker.patch("instagram_private_api.client.Client.login", return_value=None)
    return DirectEndpoint(random_string(), random_string())


@mark.parametrize(
    "data,expected",
    [
        [1, "[[1]]"],
        [[1, 2, 3], "[[1,2,3]]"],
    ],
)
def test_convert_recipient(data, expected):
    assert DirectEndpoint._convert_recipient_users(data) == expected


class TestSendItem:
    @fixture
    def response(self):
        r = Response()
        r._content = b'{"key": "value"}'
        return r

    @fixture
    def mock_post(self, mocker, response):
        return mocker.patch("requests.post", return_value=response)

    def test_send_item(self, mock_post, direct_endpoint, response):
        response.status_code = 200

        data = direct_endpoint.direct_v2_send_item(
            recipient_users=1,
            item_type="text",
            item_data={},
        )

        assert data == {"key": "value"}

        _, kwargs = mock_post.call_args
        assert "thread_ids" not in kwargs["data"]

    def test_send_item_with_thread_id(self, mock_post, direct_endpoint, response):
        response.status_code = 200

        data = direct_endpoint.direct_v2_send_item(
            recipient_users=1,
            thread_id=1,
            item_type="text",
            item_data={},
        )

        assert data == {"key": "value"}

        _, kwargs = mock_post.call_args
        assert "thread_ids" in kwargs["data"]

    def test_send_item_raise_exception(self, mock_post, direct_endpoint, response):
        response.status_code = 400

        with raises(ClientError):
            direct_endpoint.direct_v2_send_item(
                recipient_users=1,
                thread_id=1,
                item_type="text",
                item_data={},
            )


@mark.parametrize(
    "method,kwargs",
    [
        [DirectEndpoint.direct_v2_send_media_share, {"media_id": 1}],
        [DirectEndpoint.direct_v2_send_hashtag, {"hashtag": ""}],
        [DirectEndpoint.direct_v2_send_profile, {"profile_id": 1}],
        [DirectEndpoint.direct_v2_send_link, {"link": ""}],
        [DirectEndpoint.direct_v2_send_text, {"text": ""}],
    ],
)
def test_custom_send(mocker, method, direct_endpoint, kwargs):
    mock = mocker.patch("instapi.client_api.direct.DirectEndpoint.direct_v2_send_item")
    method(direct_endpoint, **kwargs)

    mock.assert_called_once()


@mark.parametrize(
    "method,kwargs",
    [
        [DirectEndpoint.direct_v2_inbox, {}],
        [DirectEndpoint.direct_v2_get_by_participants, {"recipient_users": 1}],
        [DirectEndpoint.direct_v2_thread, {"thread_id": 1}],
    ],
)
def test_direct_call_api(mocker, method, direct_endpoint, kwargs):
    mock = mocker.patch("instapi.client_api.direct.DirectEndpoint._call_api")
    method(direct_endpoint, **kwargs)

    mock.assert_called_once()
