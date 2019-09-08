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
    asdict,
    dataclass,
    field,
    Field,
)

from instapi.client import client

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

    def as_dict(self) -> Dict[str, Any]:
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
class Entity(BaseModel):
    pk: int = field(repr=False)

    def __hash__(self) -> int:
        return hash(self.pk)

    @classmethod
    def create(cls: Type[ModelT_co], data: Dict[str, Any]) -> ModelT_co:
        return super().create(data)


@dataclass(frozen=True)
class Media(Entity):

    def _media_info(self) -> Dict[str, Any]:
        items, *_ = client.media_info(self.pk)['items']
        return cast(Dict[str, Any], items)


__all__ = [
    'BaseModel',
    'Entity',
    'Media',
    'ModelT_co',
]
