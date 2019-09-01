from functools import lru_cache
from typing import (
    AbstractSet,
    Any,
    cast,
    ClassVar,
    Dict,
    Type,
    TypeVar,
)

from dataclasses import (
    dataclass,
    field,
    Field,
)

from instapi.client import client

ModelT = TypeVar('ModelT')


@dataclass(frozen=True)
class BaseModel:
    __dataclass_fields__: ClassVar[Dict[str, Field]]

    @classmethod
    @lru_cache()
    def fields(cls) -> AbstractSet[str]:
        return cls.__dataclass_fields__.keys() - {'__dataclass_fields__'}

    @classmethod
    def create(cls: Type[ModelT], data: Dict[str, Any]) -> ModelT:
        # noinspection PyArgumentList
        return cls(**{k: data[k] for k in cls.fields()})  # type: ignore


@dataclass(frozen=True)
class Entity(BaseModel):
    pk: int = field(repr=False)

    def __hash__(self) -> int:
        return hash(self.pk)


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> Dict[str, Any]:
        items, *_ = client.media_info(self.pk)['items']
        return cast(Dict[str, Any], items)


__all__ = [
    'BaseModel',
    'Entity',
    'Media',
]
