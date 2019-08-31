import ssl
from typing import (
    cast,
    ClassVar,
)

from dataclasses import dataclass
from instagram_private_api import Client as BaseClient

from instapi.exceptions import ClientNotInitedException

ssl._create_default_https_context = ssl._create_unverified_context


@dataclass
class ClientProxy:
    obj: BaseClient = None

    # Used to return dummy implementation of methods
    is_testing: ClassVar[bool] = False

    def __getattr__(self, item):
        if self.obj is None:
            if self.is_testing:
                return None

            raise ClientNotInitedException()

        return getattr(self.obj, item)


client: BaseClient = cast(BaseClient, ClientProxy())


def bind(username: str, password: str) -> None:
    client.obj = BaseClient(username, password)


__all__ = [
    'bind',
    'client',
    'ClientProxy',
]
