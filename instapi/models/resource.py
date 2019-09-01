import io
from pathlib import Path
from shutil import copyfileobj
from typing import Union
from urllib.parse import urlparse

from dataclasses import dataclass
from PIL import Image as PILImage
from requests import get

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
    def file_path(self) -> Path:
        """
        Return the name of image/video

        :return: path to file
        """
        *_, file_name = urlparse(self.url).path.split('/')
        return Path(file_name)

    def download(self, into: Path = None) -> None:
        """
        Download image/video

        :param into: path for storage file
        :return: None
        """
        into = into or self.file_path
        response = get(self.url, stream=True)

        with into.open(mode='wb') as f:
            copyfileobj(response.raw, f)


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
        response = get(self.url)
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
