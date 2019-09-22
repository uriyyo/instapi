class TestStory:
    def test_mark_seen(self, mocker, story):
        media_info = {}
        mocker.patch('instapi.models.Media._media_info', return_value=media_info)
        mock = mocker.patch('instapi.client.client.media_seen')

        story.mark_seen()

        mock.assert_called_once_with([media_info])

    def test_as_dict(self, story):
        data = story.as_dict()

        assert 'reel_mentions' in data
        assert data['reel_mentions'] == story.mentions
