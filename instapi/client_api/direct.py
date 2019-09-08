from typing import (
    cast,
    Iterable,
    SupportsInt,
    Union,
)

import requests
from instagram_private_api.errors import ClientError

from instapi.client_api.base import BaseClient
from instapi.types import (
    StrDict,
    SupportsInt_co,
)
from instapi.utils import join

RecipientUsers = Union[SupportsInt_co, Iterable[SupportsInt_co]]


class DirectEndpoint(BaseClient):
    @staticmethod
    def _convert_recipient_users(
            recipient_users: RecipientUsers,
            braces_count: int = 2,
    ) -> str:
        try:
            value = join(map(int, cast(Iterable, recipient_users)))
        except TypeError:
            value = str(recipient_users)

        return f'{"[" * braces_count}{value}{"]" * braces_count}'

    def direct_v2_send_item(
            self,
            recipient_users: RecipientUsers,
            thread_id: int = None,
            *,
            item_type: str,
            item_data: StrDict,
            version: str = 'v1',
    ) -> StrDict:
        url = f'{self.api_url.format(version=version)}direct_v2/threads/broadcast/{item_type}/'

        data = {
            'action': 'send_item',
            'recipient_users': self._convert_recipient_users(recipient_users),
            **item_data,
        }

        if thread_id:
            data['thread_ids'] = f'[{thread_id}]'

        response = requests.post(
            url,
            headers=self.default_headers,
            cookies=self.cookie_jar,
            data={
                **self.authenticated_params,
                **data,
            },
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise ClientError(str(e), response.status_code, response.text)

        return cast(StrDict, response.json())

    def direct_v2_send_text(
            self,
            recipient_users: RecipientUsers = (),
            thread_id: int = None,
            *,
            text: str,
    ) -> StrDict:
        return self.direct_v2_send_item(
            recipient_users=recipient_users,
            thread_id=thread_id,
            item_type='text',
            item_data={'text': text},
        )

    def direct_v2_send_link(
            self,
            recipient_users: RecipientUsers = (),
            thread_id: int = None,
            *,
            text: str = '',
            link: str
    ) -> StrDict:
        return self.direct_v2_send_item(
            recipient_users=recipient_users,
            thread_id=thread_id,
            item_type='link',
            item_data={
                'link_text': text or link,
                'link_urls': f'["{link}"]',
            },
        )

    def direct_v2_send_media_share(
            self,
            recipient_users: RecipientUsers = (),
            thread_id: int = None,
            *,
            text: str = '',
            media_type: str = 'photo',
            media_id: int,
    ) -> StrDict:
        return self.direct_v2_send_item(
            recipient_users=recipient_users,
            thread_id=thread_id,
            item_type='media_share',
            item_data={
                'text': text,
                'media_type': media_type,
                'media_id': media_id,
            },
        )

    def direct_v2_send_hashtag(
            self,
            recipient_users: RecipientUsers = (),
            thread_id: int = None,
            *,
            text: str = '',
            hashtag: str,
    ) -> StrDict:
        return self.direct_v2_send_item(
            recipient_users=recipient_users,
            thread_id=thread_id,
            item_type='hashtag',
            item_data={
                'text': text,
                'hashtag': hashtag,
            },
        )

    def direct_v2_send_profile(
            self,
            recipient_users: RecipientUsers = (),
            thread_id: int = None,
            *,
            text: str = '',
            profile_id: int,
    ) -> StrDict:
        return self.direct_v2_send_item(
            recipient_users=recipient_users,
            thread_id=thread_id,
            item_type='profile',
            item_data={
                'text': text,
                'profile_user_id': profile_id,
            },
        )

    def direct_v2_inbox(self, **kwargs: str) -> StrDict:
        return self._call_api('direct_v2/inbox', query=kwargs)

    def direct_v2_get_by_participants(self, recipient_users: RecipientUsers) -> StrDict:
        return self._call_api(
            'direct_v2/threads/get_by_participants',
            query={
                'recipient_users': self._convert_recipient_users(recipient_users, braces_count=1),
            }
        )


__all__ = [
    'DirectEndpoint',
]
