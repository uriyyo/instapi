from typing import Any
from typing import Dict
from typing import SupportsInt
from typing import TypeVar

StrDict = Dict[str, Any]
SupportsInt_co = TypeVar('SupportsInt_co', bound=SupportsInt, covariant=True)

__all__ = [
    'StrDict',
    'SupportsInt_co',
]
