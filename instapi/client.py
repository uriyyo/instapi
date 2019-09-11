import ssl
import os
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import cast

from dataclasses import dataclass

from instapi.client_api import Client
from instapi.exceptions import ClientNotInitedException

ssl._create_default_https_context = ssl._create_unverified_context

ENV_USERNAME = os.environ.get('INSTAPI_USERNAME')
ENV_PASSWORD = os.environ.get('INSTAPI_PASSWORD')


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


def bind(
        username: Optional[str] = ENV_USERNAME,
        password: Optional[str] = ENV_PASSWORD,
) -> None:
    if username is None or password is None:
        raise ValueError("Both username and password should be passed")

    client.obj = Client(username, password)


__all__ = [
    'bind',
    'client',
    'ClientProxy',
]
