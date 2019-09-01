from typing import (
    Generator,
    List,
)

from pytest import (
    fixture,
    mark,
)

from instapi.utils import (
    flat,
    limited,
    process_many,
    to_list,
)
from .conftest import random_int


class TestFlat:
    """Test for flat function"""

    def test_flat_skip_empty(self):
        # should skip empty iterables
        assert flat([[1, 2, 3], [], [4, 5], [6, 7]]) == [1, 2, 3, 4, 5, 6, 7]

    def test_flat_empty_iterable(self):
        # should work for empty list
        assert flat([]) == []

    def test_flat_dont_unpack_inner(self):
        assert flat([[1, [2]]]) == [1, [2]]


@mark.parametrize(
    'func,ret_type',
    [
        [limited, Generator],
        [to_list, List],
    ],
)
class TestLimitedAndToList:
    """
    Tests for:
    limited function
    to_list function
    """

    @fixture()
    def arr(self):
        return [*range(100)]

    def test_return_type(self, arr, func, ret_type):
        assert isinstance(func(arr), ret_type)
        assert isinstance(func(arr, limit=10), ret_type)

    @mark.usefixtures('ret_type')
    def test_without_limit(self, arr, func):
        assert [*func(arr)] == arr

    @mark.usefixtures('ret_type')
    def test_limit_bigger(self, arr, func):
        assert [*func(arr, limit=len(arr) * 5)] == arr

    @mark.usefixtures('ret_type')
    def test_limit_less(self, arr, func):
        limit = len(arr) // 2
        assert [*func(arr, limit=limit)] == arr[:limit]


class TestProcessMany:
    """Test for process_many function"""

    def test_process_many_called_once(self, mocker):
        mock = mocker.Mock(return_value={})

        _ = [*process_many(mock)]
        mock.assert_called_once_with()

    def test_process_many_with_pk(self, mocker):
        mock = mocker.Mock(return_value={})

        pk = random_int()
        _ = [*process_many(mock, pk)]

        mock.assert_called_once_with(pk)

    def test_process_many_with_rank_token(self, mocker):
        mock = mocker.Mock(return_value={})

        _ = [*process_many(mock, with_rank_token=True)]
        mock.assert_called_once()

        _, kwargs = mock.call_args
        assert 'rank_token' in kwargs
        assert isinstance(kwargs['rank_token'], str)

    def test_process_many_called_multiple_times(self, mocker):
        max_ids = [*[{'next_max_id': random_int()} for _ in range(3)], {}]
        mock = mocker.Mock(side_effect=max_ids)

        _ = [*process_many(mock)]

        mock.assert_has_calls([
            mocker.call(),
            *[mocker.call(max_id=m['next_max_id']) for m in max_ids[:-1]]
        ])

    def test_process_many_return_value(self, mocker):
        max_ids = [*[{'next_max_id': random_int()} for _ in range(3)], {}]
        mock = mocker.Mock(side_effect=max_ids)

        assert [*process_many(mock)] == max_ids
