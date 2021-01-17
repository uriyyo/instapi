from .comments import CommentsEndpoint
from .direct import DirectEndpoint


class Client(
    DirectEndpoint,
    CommentsEndpoint,
):
    pass


__all__ = [
    "Client",
]
