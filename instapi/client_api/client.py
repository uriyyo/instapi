from .direct import DirectEndpoint


class Client(
    DirectEndpoint,
):
    pass


__all__ = [
    "Client",
]
