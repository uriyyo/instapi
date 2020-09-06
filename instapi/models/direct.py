from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from dataclasses import dataclass
from dataclasses import field

from instapi.client import client
from instapi.models.base import BaseModel
from instapi.models.base import ModelT_co
from instapi.models.media import Media
from instapi.models.user import User
from instapi.types import StrDict
from instapi.utils import process_many
from instapi.utils import to_list


@dataclass(frozen=True)
class Message(BaseModel):
    item_id: int
    timestamp: int
    item_type: str
    user: User
    placeholder: StrDict = field(default_factory=dict)
    story_share: StrDict = field(default_factory=dict)

    @classmethod
    def create(cls: Type[ModelT_co], data: StrDict, cache: Dict[int, User] = None) -> ModelT_co:
        user_id = data.pop('user_id')

        if cache is not None and user_id in cache:
            user = cache[user_id]
        else:
            user = User.get(user_id)

            if cache is not None:
                cache[user_id] = user

        return super().create({'user': user, **data})

    def as_dict(self) -> StrDict:
        data = super().as_dict()
        data['user_id'] = data.pop('user')['pk']

        return data


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

    def iter_message(self) -> Iterable['Message']:
        cache: Dict[int, User] = {}

        for response in process_many(
                client.direct_v2_thread,
                self.thread_id,
                key='cursor',
                key_path='thread.oldest_cursor',
        ):
            yield from (Message.create(item, cache) for item in response['thread']['items'])

    def messages(self, limit: Optional[int] = None) -> List['Message']:
        return to_list(self.iter_message(), limit)

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
    'Message',
]
