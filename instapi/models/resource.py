import shutil
from pathlib import Path
from typing import (
    Any,
    Dict,
    IO,
    Iterable,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)
from urllib.parse import urlparse

import requests
from dataclasses import (
    dataclass,
    field,
)
from PIL import Image as PILImage

from instapi.models.base import (
    BaseModel,
    ModelT_co,
)


@dataclass(frozen=True, order=True)
class Candidate(BaseModel):
    """
    Represent a candidate for Resource
    """
    width: int
    height: int
    url: str = field(compare=False)

    @property
    def filename(self) -> Path:
        """
        Return the name of image/video

        :return: path to file
        """
        *_, filename = urlparse(self.url).path.split('/')
        return Path(filename)

    def content(self) -> IO[bytes]:
        """
        File-like object, which contains candidate content

        :return: candidate content
        """
        response = requests.get(self.url, stream=True)
        return cast(IO[bytes], response.raw)

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
            into = Path(filename)

        with into.open(mode='wb') as f:
            shutil.copyfileobj(self.content(), f)


@dataclass(frozen=True)
class Resource(BaseModel):
    """
    This class represents image or video, which contains in the post
    """
    candidates: Tuple[Candidate]

    def __post_init__(self) -> None:
        if not self.candidates:
            raise ValueError("Candidates can't be empty")

    @classmethod
    def create(cls: Type[ModelT_co], data: Iterable[Dict[str, Any]]) -> ModelT_co:
        """
        Create Resource from iterable of candidates

        :param data: iterable of candidates
        :return: resources with given candidates
        """
        candidates = tuple(Candidate.create(c) for c in data)
        return cls(candidates)  # type: ignore

    @property
    def best_candidate(self) -> Candidate:
        """
        Return the best available candidate for given resource

        :return: the best candidate
        """
        return max(self.candidates)

    def download(
            self,
            directory: Path = None,
            filename: Union[Path, str] = None,
            candidate: Candidate = None,
    ) -> None:
        """
        Download image/video

        :param candidate: candidate to use or None
        :param directory: path for storage file
        :param filename: name of file, which will be downloaded
        :return: None
        """
        candidate = candidate or self.best_candidate
        candidate.download(directory, filename)

    @classmethod
    def create_resources(
            cls,
            resources_data: Iterable[Dict[str, Any]],
            video: bool = True,
            image: bool = True,
    ) -> Iterable['Resources']:
        """
        Create a generator for iteration over images/videos, which contains in the resources_data

        :param resources_data: iterable with information about resources
        :param video: true - add videos, false - ignore videos
        :param image: true - add images, false - ignore images
        :return: generator with images/videos
        """
        for data in resources_data:
            if (video and cls.is_video_data(data)) or (image and cls.is_image_data(data)):
                resource = cls.from_data(data)

                if resource is not None:
                    yield resource

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Optional['Resources']:
        """
        Create resource based on data fetched from api

        :param data: data from api
        :return: resource instance or None
        """
        if cls.is_video_data(data):
            return Video.create(data['video_versions'])
        elif cls.is_image_data(data):
            return Image.create(data['image_versions2']['candidates'])
        else:
            return None

    @staticmethod
    def is_video_data(data: Dict[str, Any]) -> bool:
        """
        Check if given data contains information about video resource

        :param data: resource data
        :return: is given data contains information about video resource
        """
        return 'video_versions' in data

    @staticmethod
    def is_image_data(data: Dict[str, Any]) -> bool:
        """
        Check if given data contains information about image resource

        :param data: resource data
        :return: is given data contains information about image resource
        """
        return 'video_versions' not in data and 'image_versions2' in data


@dataclass(frozen=True)
class Video(Resource):
    """
    This class represents video resource
    """

    def as_dict(self) -> Dict[str, Any]:
        return {
            'video_versions': [c.as_dict() for c in self.candidates]
        }


@dataclass(frozen=True)
class Image(Resource):
    """
    This class represents image resource
    """

    def as_dict(self) -> Dict[str, Any]:
        return {
            'image_versions2': {
                'candidates': [c.as_dict() for c in self.candidates]
            }
        }

    def preview(self, candidate: Candidate = None) -> None:
        """
        Show preview of image

        :param candidate: candidate to preview or None
        :return: None
        """
        candidate = candidate or self.best_candidate

        img = PILImage.open(candidate.content())
        img.show()


Resources = Union[Image, Video]

__all__ = [
    'Candidate',
    'Resource',
    'Resources',
    'Video',
    'Image',
]
