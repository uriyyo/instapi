import ssl
from typing import (
    Any,
    cast,
    ClassVar,
    Optional,
)

from dataclasses import dataclass

from instapi.client_api import Client
from instapi.exceptions import ClientNotInitedException

ssl._create_default_https_context = ssl._create_unverified_context


@dataclass
class ClientProxy:
    obj: Optional[Client] = None

    # Used to return dummy implementation of methods
    is_testing: ClassVar[bool] = False

    def __getattr__(self, item: str) -> Any:
        if self.obj is None:
            if self.is_testing:
                return None

            raise ClientNotInitedException()

        return getattr(self.obj, item)


client: Client = cast(Client, ClientProxy())


def bind(username: str, password: str) -> None:
    client.obj = Client(username, password)


__all__ = [
    'bind',
    'client',
    'ClientProxy',
]
