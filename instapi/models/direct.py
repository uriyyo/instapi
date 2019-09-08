from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import (
    BaseModel,
    Media,
    ModelT_co,
)
from instapi.models.user import User
from instapi.types import StrDict
from instapi.utils import (
    process_many,
    to_list,
)


@dataclass(frozen=True)
class Direct(BaseModel):
    thread_title: str
    thread_type: str
    is_group: bool
    users: Tuple[User]
    thread_id: Optional[int] = None

    @classmethod
    def create(cls: Type[ModelT_co], data: Any) -> ModelT_co:
        return super().create({
            **data,
            'users': tuple(map(User.create, data['users'])),
        })

    @classmethod
    def iter_directs(cls) -> Iterable['Direct']:
        for response in process_many(client.direct_v2_inbox, key='cursor', key_path='inbox.oldest_cursor'):
            yield from map(Direct.create, response['inbox']['threads'])

    @classmethod
    def directs(cls, limit: Optional[int] = None) -> List['Direct']:
        return to_list(cls.iter_directs(), limit)

    @classmethod
    def with_user(cls: Type[ModelT_co], user: User) -> ModelT_co:
        result = client.direct_v2_get_by_participants(user)

        try:
            return cls.create(result['thread'])
        except KeyError:
            return cls(user.username, 'private', False, (user,))  # type: ignore

    @property
    def _send_args(self) -> StrDict:
        return {
            'recipient_users': self.users,
            'thread_id': self.thread_id,
        }

    def send_text(self, text: str) -> None:
        client.direct_v2_send_text(
            text=text,
            **self._send_args,
        )

    def send_link(self, link: str, text: str = '') -> None:
        client.direct_v2_send_link(
            link=link,
            text=text,
            **self._send_args,
        )

    def send_profile(self, user: User, text: str = '') -> None:
        client.direct_v2_send_profile(
            text=text,
            profile_id=user.pk,
            **self._send_args,
        )

    def send_hashtag(self, hashtag: str, text: str = '') -> None:
        client.direct_v2_send_hashtag(
            hashtag=hashtag,
            text=text,
            **self._send_args,
        )

    def send_media(self, media: Media, text: str = '') -> None:
        client.direct_v2_send_media_share(
            text=text,
            media_id=media.pk,
            **self._send_args,
        )


__all__ = [
    'Direct',
]
