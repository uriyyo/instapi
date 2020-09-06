from dataclasses import dataclass

from pytest import fixture, raises

from instapi.models.base import BaseModel
from tests.unit_tests.conftest import random_int, random_string


class TestBaseModel:
    """Tests for BaseModel class"""

    @fixture()
    def model_cls(self):
        @dataclass(frozen=True)
        class TempModel(BaseModel):
            a: int
            b: int
            c: int

        return TempModel

    @fixture()
    def mocked_fields(self, mocker):
        fields = {"a", "b", "c"}
        mocker.patch("instapi.models.base.BaseModel.fields", return_value=fields)
        data = {key: random_int() for key in fields}

        return data

    def test_fields(self, model_cls):
        """Test for BaseModel.fields classmethod"""

        assert model_cls.fields() == {"a", "b", "c"}

    def test_fields_with_inheritance(self):
        """Test for BaseModel.fields classmethod"""

        @dataclass(frozen=True)
        class First(BaseModel):
            a: int

        assert First.fields() == {"a"}

        @dataclass(frozen=True)
        class Two(First):
            b: int

        assert Two.fields() == {"a", "b"}

        @dataclass(frozen=True)
        class Three(Two):
            c: int

        assert Three.fields() == {"a", "b", "c"}

    def test_create(self, model_cls, mocked_fields):
        assert model_cls.create(mocked_fields) == model_cls(**mocked_fields)

    def test_create_data_has_more_fields(self, model_cls, mocked_fields):
        more_fields = {**mocked_fields, random_string(): random_int()}

        assert model_cls.create(more_fields) == model_cls(**mocked_fields)

    def test_create_data_has_less_fields(self, model_cls, mocked_fields):
        less_fields = {key: mocked_fields[key] for key in [*mocked_fields][:-1]}

        with raises(Exception):
            model_cls.create(less_fields)


class TestEntity:
    """Tests for Entity class"""

    def test_entity_hash(self, entity):
        # Entity hash should be calculated base on pk field
        assert hash(entity) == hash(entity.pk)

    def test_entity_support_int(self, entity):
        assert entity.pk == int(entity)
