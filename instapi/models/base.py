from functools import lru_cache
from typing import (
    Any,
    ClassVar,
    Dict,
    Set,
)

from dataclasses import (
    dataclass,
    field,
)

from instapi.client import client


@dataclass(frozen=True)
class BaseModel:
    __dataclass_fields__: ClassVar[Dict]

    @classmethod
    @lru_cache()
    def fields(cls) -> Set[str]:
        return cls.__dataclass_fields__.keys() - {'__dataclass_fields__'}

    @classmethod
    def create(cls, data: Dict[str, Any]):
        # noinspection PyArgumentList
        return cls(**{k: data[k] for k in cls.fields()})


@dataclass(frozen=True)
class Entity(BaseModel):
    pk: int = field(repr=False)

    def __hash__(self):
        return hash(self.pk)


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> Dict[str, Any]:
        items, *_ = client.media_info(self.pk)['items']
        return items


__all__ = [
    'BaseModel',
    'Entity',
    'Media',
]
