from typing import Any, Iterator, Union

from ..types import StrDict
from .base import BaseClient


class CommentsEndpoint(BaseClient):
    def media_comments_gen(self, media_id: Union[int, str], **kwargs: Any) -> Iterator[StrDict]:
        kwargs.setdefault("can_support_threading", "false")

        results = self.media_comments(media_id, **kwargs)
        yield from results["comments"]

        while any(
            (
                results.get("has_more_comments") and results.get("next_max_id"),
                results.get("has_more_headload_comments") and results.get("next_min_id"),
            )
        ):
            if results.get("has_more_comments"):
                kwargs["max_id"] = results.get("next_max_id")
            else:
                kwargs["min_id"] = results.get("next_min_id")

            results = self.media_comments(media_id, **kwargs)
            yield from results["comments"]


__all__ = ["CommentsEndpoint"]
