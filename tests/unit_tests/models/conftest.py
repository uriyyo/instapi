from functools import partial
from typing import List

from pytest import fixture

from instapi.models import (
    Comment,
    Entity,
    Feed,
    Media,
    User,
)
from instapi.models.resource import (
    Image,
    Resource,
    Video,
)
from ..conftest import (
    rand,
    random_url,
    rands,
)


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


def create_resource(length: int = 10) -> List[Resource]:
    """
    Generate list of dummy resources

    :param length: length of list
    :return: list of dummy resources
    """
    return rands(Resource, length, url=random_url)


def create_images(length: int = 10) -> List[Image]:
    """
    Generate list of dummy images

    :param length: length of list
    :return: list of dummy images
    """
    return rands(Image, length, url=random_url)


def create_comments(length: int = 10) -> List[Comment]:
    """
    Generate list of dummy comments

    :param length: length of list
    :return: list of dummy comments
    """
    return [
        Comment(
            text=random_string(),
            user=vars(create_users(length=1)[0]),
            pk=random_int(),
        ) for _ in range(length)
    ]


def create_feeds(length: int = 10) -> List[Feed]:
    """
    Generate list of dummy feeds

    :param length: length of list
    :return: list of dummy feeds
    """
    return [
        Feed(
            like_count=random_int(),
            comment_count=random_int(),
            pk=random_int(),
        ) for _ in range(length)
    ]


def create_videos(length: int = 10) -> List[Video]:
    """
    Generate list of dummy videos

    :param length: length of list
    :return: list of dummy videos
    """
    return rands(Video, length, url=partial(random_url, '.mp4'))


@fixture()
def user() -> User:
    """Fixture that return dummy user"""
    u, = create_users(length=1)
    return u


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
def comment(user) -> Comment:
    """Fixture that return comment with random content"""
    return rand(Comment)
