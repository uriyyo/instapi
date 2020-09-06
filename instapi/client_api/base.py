from typing import Any, Dict, cast

from instagram_private_api import Client

from ..types import StrDict


class BaseClient(Client):
    def _call_api(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        query: Dict[str, Any] = None,
        return_response: bool = False,
        unsigned: bool = False,
        version: str = "v1",
    ) -> StrDict:
        value = super()._call_api(
            endpoint=endpoint,
            params=params,
            query=query,
            return_response=return_response,
            unsigned=unsigned,
            version=version,
        )

        return cast(StrDict, value)


__all__ = [
    "BaseClient",
]
