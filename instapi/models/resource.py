import io
from pathlib import Path
from shutil import copyfileobj
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

    def preview(self):
        response = get(self.url)
        image = io.BytesIO(response.content)
        img = Image.open(image)
        img.show()


__all__ = [
    'Resource',
]
