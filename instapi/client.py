import os
import ssl
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, cast

from instagram_private_api import ClientError

from . import cache
from .client_api import Client
from .exceptions import ClientNotInitedException

ssl._create_default_https_context = ssl._create_unverified_context

ENV_USERNAME = os.environ.get("INSTAPI_USERNAME")
ENV_PASSWORD = os.environ.get("INSTAPI_PASSWORD")


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

    try:
        client.obj = Client(username, password, cookie=cache.get_from_cache((username, password)))
    except ClientError:  # pragma: no cover
        client.obj = Client(username, password)

    cache.write_to_cache((username, password), client.obj.cookie_jar)


__all__ = [
    "bind",
    "client",
    "ClientProxy",
]
