import io
from pathlib import Path
from string import ascii_letters

from pytest import (
    fixture,
    mark,
)
from requests import Response

from instapi import Resource
from ..conftest import (
    random_bytes,
    random_string,
)


class TestImage:
    """
    Test for Image class
    """

    def test_image(self, mocker, image):
        image_content = random_bytes()
        response = Response()
        response._content = image_content

        get_mock = mocker.patch('requests.get', return_value=response)
        image_mock = mocker.Mock()
        open_mock = mocker.patch('PIL.Image.open', return_value=image_mock)

        image.preview()

        get_mock.assert_called_once_with(image.url)
        assert open_mock.call_args[0][0].read() == image_content
        open_mock.show.called_once()


class TestResource:
    """
    Test for Resource class
    """

    @fixture()
    def get_mocker(self, mocker):
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
    def test_file_path(self, resource, url, filename):
        r = Resource(url, 0, 0)
        assert r.filename == Path(filename)
