import io
from pathlib import Path

from pytest import (
    fixture,
    mark,
    raises,
)

from instapi import Resource
from instapi.models.resource import Candidate
from ..conftest import (
    random_bytes,
    random_string,
)


@fixture
def mock_content(mocker):
    content = random_bytes()
    mock = mocker.patch('instapi.Candidate.content', side_effect=lambda: io.BytesIO(content))

    return mock, content


class TestImage:
    """
    Test for Image class
    """

    @mark.usefixtures('mock_content')
    def test_image(self, mocker, image):
        open_mock = mocker.patch('PIL.Image.open')

        image.preview()

        open_mock.show.called_once()


class TestCandidate:
    """
    Test for Candidate class
    """

    @fixture
    def mock_requests_get(self, mocker):
        resource_content = random_bytes()
        get_mock = mocker.patch(
            'requests.get',
            return_value=mocker.Mock(raw=io.BytesIO(resource_content)),
        )
        return get_mock, resource_content

    @mark.parametrize(
        'url,filename',
        [
            ['http://instapi.com/sasha.jpg', 'sasha.jpg'],
            ['https://instapi/images/thumb/5/not-sasha.jpg/this-is-sasha.jpg', 'this-is-sasha.jpg'],
            ['https://instapi/images/sasha.jpg?age=too_old&for=school', 'sasha.jpg'],
        ]
    )
    def test_filename(self, resource, url, filename):
        r = Candidate(0, 0, url)
        assert r.filename == Path(filename)

    def test_candidate_content(self, mock_requests_get, candidate):
        get_mock, resource_content = mock_requests_get
        content = candidate.content()

        assert content.read() == resource_content

        get_mock.assert_called_with(candidate.url, stream=True)

    @mark.usefixtures('mock_content')
    def test_download_without_param(self, tmp_path, candidate):
        candidate.download()

        assert candidate.filename.exists()

        candidate.filename.unlink()

    @mark.usefixtures('mock_content')
    def test_download_with_path(self, tmp_path, candidate):
        candidate.download(tmp_path)
        result_path: Path = tmp_path / candidate.filename

        assert result_path.exists()

    @mark.usefixtures('mock_content')
    def test_download_with_path_and_filename(self, tmp_path, resource):
        rand_filename = random_string() + '.jpg'
        resource.download(tmp_path, rand_filename)
        result_path: Path = tmp_path / rand_filename

        assert result_path.exists()


class TestResource:
    """
    Test for Resource class
    """

    @mark.parametrize(
        'data',
        [
            [{}],
            [{'invalid_key': []}],
        ]
    )
    def test_from_data_invalid_data(self, data):
        assert Resource.from_data(data) is None

    def test_resource_with_no_candidates(self):
        with raises(ValueError):
            Resource(())


class TestResourceContainer:

    @fixture
    def mock_images(self, mocker, images):
        return mocker.patch(
            'instapi.models.media.Media._media_info',
            return_value=images[0].as_dict(),
        )

    @fixture
    def mock_videos(self, mocker, videos):
        return mocker.patch(
            'instapi.models.media.Media._media_info',
            return_value=videos[0].as_dict(),
        )

    def test_resources(self, mocker, resource_container):
        mock = mocker.patch('instapi.models.media.Media._media_info')

        resource_container._resources()

        mock.assert_called_once()

    def test_iter_resources_videos_without_carusel(self, mock_videos, videos, feed):
        assert [*feed.iter_resources()] == videos

    def test_iter_resources_images_without_carusel(self, mock_images, images, feed):
        assert [*feed.iter_resources()] == images

    def test_resources_videos(self, mock_videos, videos, feed):
        assert feed.resources() == videos

    def test_resources_images(self, mock_images, images, feed):
        assert feed.resources() == images

    def test_iter_videos(self, mock_videos, videos, feed):
        assert [*feed.iter_videos()] == videos

    def test_videos(self, mock_videos, videos, feed):
        assert feed.videos() == videos

    def test_iter_images(self, mock_images, images, feed):
        assert [*feed.iter_images()] == images

    def test_images(self, mock_images, images, feed):
        assert feed.images() == images

    def test_video(self, mock_videos, videos, feed):
        assert feed.video() == videos[0]

    def test_image(self, mock_images, images, feed):
        assert feed.image() == images[0]
