import ssl

from instagram_private_api import Client as BaseClient
from lazy_object_proxy import Proxy

ssl._create_default_https_context = ssl._create_unverified_context
client: BaseClient = Proxy(lambda: None)


def bind(username: str, password: str) -> None:
    client.__wrapped__ = BaseClient(username, password)
