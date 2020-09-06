def test_like_comment(comment, mocker):
    """Test for Comment.like method"""
    like_mock = mocker.patch("instapi.client.client.comment_like")

    comment.like()

    like_mock.assert_called_once_with(comment.pk)


def test_unlike_comment(comment, mocker):
    """Test for Comment.unlike method"""
    unlike_mock = mocker.patch("instapi.client.client.comment_unlike")

    comment.unlike()

    unlike_mock.assert_called_once_with(comment.pk)
