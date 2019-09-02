import io

from pytest import fixture, mark
from string import ascii_letters
from instapi import Resource
from .conftest import (
    create_images,
    create_resource,
)

from ..conftest import random_bytes, random_string

from requests import Response
from pathlib import Path


class TestImage:
    """
    Test for Image class
    """

    @fixture()
    def image(self):
        im, = create_images(length=1)
        return im

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
    def resource(self):
        resp, = create_resource(length=1)
        return resp

    @fixture()
    def response(self):
        resource_content = random_bytes()
        response = Response()
        response.raw = io.BytesIO(resource_content)

    def test_download_with_path(self, tmp_path, mocker, resource):
        resource_content = random_bytes()
        response = Response()
        response.raw = io.BytesIO(resource_content)

        get_mock = mocker.patch('requests.get', return_value=response)

        resource.download(tmp_path)
        result_path: Path = tmp_path / resource.filename

        assert result_path.exists()
        get_mock.assert_called_once_with(resource.url, stream=True)

    def test_download_with_path_and_filename(self, mocker, tmp_path, resource):
        resource_content = random_bytes()
        response = Response()
        response.raw = io.BytesIO(resource_content)

        get_mock = mocker.patch('requests.get', return_value=response)

        rand_filename = random_string(source=ascii_letters) + '.jpg'

        resource.download(tmp_path, rand_filename)
        result_path: Path = tmp_path / rand_filename

        assert result_path.exists()
        get_mock.assert_called_once_with(resource.url, stream=True)

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
