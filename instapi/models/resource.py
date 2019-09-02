import io
import requests
import shutil

from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from dataclasses import dataclass
from PIL import Image as PILImage

from instapi.models.base import BaseModel


@dataclass(frozen=True)
class Resource(BaseModel):
    """
    This class represents image or video, which contains in the post
    """
    url: str
    width: int
    height: int

    @property
    def filename(self) -> Path:
        """
        Return the name of image/video

        :return: path to file
        """
        *_, filename = urlparse(self.url).path.split('/')
        return Path(filename)

    def download(self, directory: Path = None, filename: Union[Path, str] = None) -> None:
        """
        Download image/video

        :param directory: path for storage file
        :param filename: name of file, which will be downloaded
        :return: None
        """
        filename = filename or self.filename

        if directory:
            into = directory / filename
        else:
            into = filename

        response = requests.get(self.url, stream=True)

        with into.open(mode='wb') as f:
            shutil.copyfileobj(response.raw, f)


@dataclass(frozen=True)
class Video(Resource):
    """
    This class represents video resource
    """
    ...


@dataclass(frozen=True)
class Image(Resource):
    """
    This class represents image resource
    """
    def preview(self) -> None:
        """
        Show preview of image

        :return: None
        """
        response = requests.get(self.url)
        image = io.BytesIO(response.content)
        img = PILImage.open(image)
        img.show()


Resources = Union[Image, Video]

__all__ = [
    'Resource',
    'Resources',
    'Video',
    'Image',
]
