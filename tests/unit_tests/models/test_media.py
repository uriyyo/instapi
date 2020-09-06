from ..conftest import random_string


class TestMedia:
    """Tests for Media class"""

    def test_media_info(self, media, mocker):
        items = [[*range(100)]]
        data = {'items': items}

        media_info_mock = mocker.patch('instapi.client.client.media_info', return_value=data)

        assert media._media_info() == items[0]
        media_info_mock.assert_called_once_with(media.pk)

    def test_comment(self, mocker, media):
        comment_mock = mocker.patch('instapi.client.client.post_comment')
        text = random_string()

        media.comment(text)

        comment_mock.assert_called_once_with(media.pk, text)
