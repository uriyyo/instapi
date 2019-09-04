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
    random_int,
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
    return rands(Comment, length)


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
    # User id must not be in range from 1 to 100 because
    # randomly generated users have same the range
    # so user fixture will return user with pk in range
    # from 101 to 200 to avoid fails at random tests
    return rand(User, pk=partial(random_int, 101, 200))


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
