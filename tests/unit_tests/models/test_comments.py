from instapi.client import client


def test_like_comment(comment, mocker):
    """Test for Comment.like method"""
    mocker.patch('instapi.client.client.comment_like')

    comment.like()
    client.comment_like.assert_called_once_with(comment.pk)


def test_unlike_comment(comment, mocker):
    """Test for Comment.unlike method"""
    mocker.patch('instapi.client.client.comment_unlike')

    comment.unlike()

    client.comment_unlike.assert_called_once_with(comment.pk)
