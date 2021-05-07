from pytest import fixture, mark

from instapi.client_api.comments import CommentsEndpoint
from instapi.utils import flat

from ..conftest import random_int, random_string


@fixture
def comments_endpoint(mocker):
    mocker.patch("instagram_private_api.client.Client.login", return_value=None)
    return CommentsEndpoint(random_string(), random_string())


def test_comments_gen_no_more_comments(comments_endpoint, mocker):
    mock = mocker.patch.object(
        comments_endpoint, "media_comments", autospec=True, return_value={"comments": []}
    )

    media_id = random_int()

    assert not [*comments_endpoint.media_comments_gen(media_id)]

    mock.assert_called_once_with(media_id, can_support_threading="false")


@mark.parametrize(
    "indicator,key,next_key",
    [
        ("has_more_comments", "max_id", "next_max_id"),
        ("has_more_headload_comments", "min_id", "next_min_id"),
    ],
    ids=["max_id", "min_id"],
)
def test_comments_gen_next_comments(comments_endpoint, mocker, indicator, key, next_key):
    side_effects = [
        {
            "comments": [mocker.Mock() for _ in range(10)],
            indicator: True,
            next_key: mocker.Mock(),
        }
        for _ in range(10)
    ]
    side_effects[-1][indicator] = False

    mock = mocker.patch.object(
        comments_endpoint, "media_comments", autospec=True, side_effect=side_effects
    )

    comments = [*flat(r["comments"] for r in side_effects)]

    media_id = random_int()

    assert [*comments_endpoint.media_comments_gen(media_id)] == comments

    calls = [mocker.call(media_id, can_support_threading="false")]
    calls.extend(
        mocker.call(
            media_id,
            can_support_threading="false",
            **{key: r[next_key]},
        )
        for r in side_effects[:-1]
    )

    mock.assert_has_calls(calls)
