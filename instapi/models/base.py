from dataclasses import asdict, dataclass, field, fields
from typing import AbstractSet, Any, Type, TypeVar, cast

from ..types import StrDict

ModelT_co = TypeVar("ModelT_co", bound="BaseModel", covariant=True)


@dataclass(frozen=True)
class BaseModel:
    @classmethod
    def fields(cls) -> AbstractSet[str]:
        return {f.name for f in fields(cls)} - {"__dataclass_fields__"}

    @classmethod
    def create(cls: Type[ModelT_co], data: Any) -> ModelT_co:
        # noinspection PyArgumentList
        return cast(ModelT_co, cls(**{k: data[k] for k in cls.fields() if k in data}))  # type: ignore

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
class Entity(BaseModel):
    pk: int = field(repr=False)

    def __hash__(self) -> int:
        return hash(self.pk)

    def __int__(self) -> int:
        return self.pk

    @classmethod
    def create(cls: Type[ModelT_co], data: StrDict) -> ModelT_co:
        return super().create(data)  # type: ignore


__all__ = [
    "BaseModel",
    "Entity",
    "ModelT_co",
]
