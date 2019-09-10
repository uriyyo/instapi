from functools import lru_cache
from typing import AbstractSet
from typing import Any
from typing import ClassVar
from typing import Dict
from typing import SupportsInt
from typing import Type
from typing import TypeVar
from typing import cast

from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from instapi.client import client
from instapi.types import StrDict

ModelT_co = TypeVar('ModelT_co', bound='BaseModel', covariant=True)


@dataclass(frozen=True)
class BaseModel:
    __dataclass_fields__: ClassVar[Dict[str, Field]]

    @classmethod
    @lru_cache()
    def fields(cls) -> AbstractSet[str]:
        return cls.__dataclass_fields__.keys() - {'__dataclass_fields__'}

    @classmethod
    def create(cls: Type[ModelT_co], data: Any) -> ModelT_co:
        # noinspection PyArgumentList
        return cls(**{k: data[k] for k in cls.fields() if k in data})  # type: ignore

    def as_dict(self) -> StrDict:
        """
        Convert model into native instagram representation.
        Should be overridden at delivered classes if model
        has specific representation.

        :return: native instagram representation
        """
        return {
            key: value.as_dict() if isinstance(value, BaseModel) else value
            for key, value in asdict(self).items()
        }


@dataclass(frozen=True)
class Entity(BaseModel, SupportsInt):
    pk: int = field(repr=False)

    def __hash__(self) -> int:
        return hash(self.pk)

    def __int__(self) -> int:
        return self.pk

    @classmethod
    def create(cls: Type[ModelT_co], data: StrDict) -> ModelT_co:
        return super().create(data)


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> StrDict:
        items, *_ = client.media_info(self.pk)['items']
        return cast(StrDict, items)


__all__ = [
    'BaseModel',
    'Entity',
    'Media',
    'ModelT_co',
]
