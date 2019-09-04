import io
from pathlib import Path
from string import ascii_letters

from pytest import (
    fixture,
    mark,
    raises,
)
from requests import Response

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
        image_mock = mocker.Mock()
        open_mock = mocker.patch('PIL.Image.open', return_value=image_mock)

        image.preview()

        open_mock.show.called_once()


class TestCandidate:
    """
    Test for Candidate class
    """

    @fixture
    def mock_requests_get(self, mocker):
        resource_content = random_bytes()
        response = Response()
        response.raw = io.BytesIO(resource_content)

        get_mock = mocker.patch('requests.get', return_value=response)
        return get_mock

    @mark.parametrize(
        'data',
        [
            [{}],
            [{'invalid_key': []}],
        ]
    )
    def test_from_data_invalid_data(self, data):
        assert Resource.from_data(data) is None

    def test_download_without_param(self, tmp_path, get_mocker, resource):
        resource.download()

        assert resource.filename.exists()
        resource.filename.unlink()

        get_mocker.assert_called_once_with(resource.url, stream=True)

    def test_download_with_path(self, tmp_path, get_mocker, resource):
        resource.download(tmp_path)
        result_path: Path = tmp_path / resource.filename

        assert result_path.exists()
        get_mocker.assert_called_once_with(resource.url, stream=True)

    def test_download_with_path_and_filename(self, get_mocker, tmp_path, resource):
        rand_filename = random_string(source=ascii_letters) + '.jpg'

        resource.download(tmp_path, rand_filename)
        result_path: Path = tmp_path / rand_filename

        assert result_path.exists()
        get_mocker.assert_called_once_with(resource.url, stream=True)

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

    def test_candidate_content(self, mocker, candidate):
        resource_content = random_bytes()
        response = mocker.Mock()
        response.raw = io.BytesIO(resource_content)
        get_mock = mocker.patch('requests.get', return_value=response)

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
        rand_filename = random_string(source=ascii_letters) + '.jpg'

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
