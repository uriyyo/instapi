from instapi.client import client


def test_like_comment(comment, mocker):
    """Test for Comment.like method"""
    mocker.patch('instapi.client.client.comment_like')

    comment.like()

    assert client.comment_like.call_count == 1

    args, kwargs = client.comment_like.call_args
    assert args == (comment.pk,)
    assert kwargs == {}


def test_unlike_comment(comment, mocker):
    """Test for Comment.unlike method"""
    mocker.patch('instapi.client.client.comment_unlike')

    comment.unlike()

    assert client.comment_unlike.call_count == 1

    args, kwargs = client.comment_unlike.call_args
    assert args == (comment.pk,)
    assert kwargs == {}
