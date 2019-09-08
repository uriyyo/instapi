from functools import partial
from random import shuffle
from typing import (
    Iterable,
    List,
    Tuple,
    Type,
    TypeVar,
)

from pytest import fixture

from instapi import Direct
from instapi.models import (
    Comment,
    Entity,
    Feed,
    Media,
    User,
)
from instapi.models.direct import Message
from instapi.models.resource import (
    Candidate,
    Image,
    Resource,
    Video,
)
from ..conftest import (
    rand,
    random_int,
    random_url,
    rands,
)

T = TypeVar('T')


def as_dicts(models: Iterable[T]) -> List[T]:
    """
    Convert models into list of their dict representations

    :param models: iterable of models
    :return: list of dicts
    """
    return [m.as_dict() for m in models]


def create_users(length: int = 10) -> List[User]:
    """
    Generate list of dummy users

    :param length: length of list
    :return: list of dummy users
    """
    return rands(User, length)


def create_feeds(length: int = 10) -> List[Feed]:
    """
    Generate list of dummy feeds

    :param length: length of list
    :return: list of dummy feeds
    """
    return rands(Feed, length)


def create_candidates(length: int = 10, extension: str = '.jpg') -> Tuple[Candidate]:
    """
    Generate list of dummy resource candidates

    :param length: length of list
    :param extension: resource extension
    :return: list of dummy candidates
    """
    return tuple(rand(Candidate, url=random_url(extension)) for _ in range(length))


def create_resource(
        length: int = 10,
        extension: str = '.jpg',
        resource_cls: Type[T] = Resource,
) -> List[T]:
    """
    Generate list of dummy resources

    :param length: length of list
    :param extension: resource extension
    :param resource_cls: resource class
    :return: list of dummy resources
    """
    return rands(
        resource_cls,
        length,
        candidates=partial(create_candidates, length=1, extension=extension),
    )


def create_images(length: int = 10) -> List[Image]:
    """
    Generate list of dummy images

    :param length: length of list
    :return: list of dummy images
    """
    return create_resource(resource_cls=Image, length=length)


def create_comments(length: int = 10) -> List[Comment]:
    """
    Generate list of dummy comments

    :param length: length of list
    :return: list of dummy comments
    """
    return rands(Comment, length)


def create_videos(length: int = 10) -> List[Video]:
    """
    Generate list of dummy videos

    :param length: length of list
    :return: list of dummy videos
    """
    return create_resource(resource_cls=Video, extension='.mp4', length=length)


def create_directs(length: int = 10) -> List[Direct]:
    return rands(
        cls=Direct,
        length=length,
        thread_id=random_int,
        users=lambda: tuple([rand(User)]),
    )


def create_messages(length: int = 10) -> List[Message]:
    # Messages should not have users with same id
    # to avoid collision will pop id from predefined
    # array of ids
    ids = [*range(length)]
    shuffle(ids)

    def user():
        return rand(User, pk=ids.pop())

    return rands(Message, length, placeholder=dict, story_share=dict, user=user)


@fixture()
def user() -> User:
    """Fixture that return dummy user"""
    # User id must not be in range from 1 to 100 because
    # randomly generated users have same the range
    # so user fixture will return user with pk in range
    # from 101 to 200 to avoid fails at random tests
    return rand(User, pk=random_int(101, 200))


@fixture()
def entity():
    """Fixture that return dummy entity"""
    return rand(Entity)


@fixture()
def media():
    """Fixture that return dummy media"""
    return rand(Media)


@fixture()
def image():
    """Fixture that return dummy image"""
    im, = create_images(length=1)
    return im


@fixture()
def resource():
    """Fixture that return dummy resource"""
    resp, = create_resource(length=1)
    return resp


@fixture()
def feed() -> Feed:
    """Fixture that return dummy feed"""
    f, = create_feeds(length=1)
    return f


@fixture()
def candidate() -> Candidate:
    """Fixture that return dummy candidate"""
    c, = create_candidates(length=1)
    return c


@fixture()
def comment(user) -> Comment:
    """Fixture that return comment with random content"""
    return rand(Comment)


@fixture
def direct(user) -> Direct:
    return rand(Direct, users=(user,), thread_id=random_int())


@fixture
def message(user) -> Message:
    return rand(Message, user=user, placeholder={}, story_share={})


@fixture
def messages() -> List[Message]:
    return create_messages()


@fixture
def directs() -> List[Direct]:
    return create_directs()


@fixture
def users():
    return create_users()


@fixture
def comments():
    return create_comments()


@fixture
def feeds():
    return create_feeds()


@fixture
def videos():
    return create_videos(length=1)


@fixture
def images():
    return create_images(length=1)
