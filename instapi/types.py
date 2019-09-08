from typing import (
    Any,
    Dict,
    SupportsInt,
    TypeVar,
)

StrDict = Dict[str, Any]
SupportsInt_co = TypeVar('SupportsInt_co', bound=SupportsInt, covariant=True)

__all__ = [
    'StrDict',
    'SupportsInt_co',
]
