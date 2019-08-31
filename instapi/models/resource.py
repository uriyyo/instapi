import io
from pathlib import Path
from shutil import copyfileobj
from typing import Union
from urllib.parse import urlparse

from dataclasses import dataclass
from PIL import Image
from requests import get

from instapi.models.base import BaseModel


@dataclass(frozen=True)
class Resource(BaseModel):
    url: str
    width: int
    height: int

    @property
    def file_path(self) -> Path:
        *_, file_name = urlparse(self.url).path.split('/')
        return Path(file_name)

    def download(self, into: Path = None) -> None:
        into = into or self.file_path
        response = get(self.url, stream=True)

        with into.open(mode='wb') as f:
            copyfileobj(response.raw, f)


@dataclass(frozen=True)
class Video(Resource):
    ...


@dataclass(frozen=True)
class Image(Resource):
    def preview(self):
        response = get(self.url)
        image = io.BytesIO(response.content)
        img = Image.open(image)
        img.show()


Resources = Union[Image, Video]

__all__ = [
    'Resource',
    'Resources',
    'Video',
    'Image',
]
