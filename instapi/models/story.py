from typing import List
from typing import Type

from dataclasses import dataclass

from instapi.client import client
from instapi.models.base import ModelT_co
from instapi.models.resource import ResourceContainer
from instapi.models.user import User
from instapi.types import StrDict


@dataclass(frozen=True)
class Story(ResourceContainer):
    """
    Class that represent user story
    """
    # TODO: Add ability to send reactions on the story

    mentions: List['User']

    @classmethod
    def create(cls: Type[ModelT_co], data: StrDict) -> ModelT_co:
        """
        Information about users mentions in a story located in reel_mentions.
        reel_mentions is a complicated name, move it to simple mentions.

        :param data: information about a story
        :return: Story instance
        """
        return super().create({
            **data,
            'mentions': [User.create(d['user']) for d in data.get('reel_mentions', ())],
        })

    def as_dict(self) -> StrDict:
        """
        Method should return dict with same structure as create method accepts.

        :return: dict with information about story
        """
        data = super().as_dict()
        data['reel_mentions'] = [{'user': user} for user in data.pop('mentions')]

        return data

    def mark_seen(self) -> None:
        """
        Mark story as seen, by default you can get story media
        and user will not know that you did that. In case when
        you want user know you watch the story this method should be called.

        :return None
        """
        client.media_seen([self._media_info()])


__all__ = [
    'Story',
]
