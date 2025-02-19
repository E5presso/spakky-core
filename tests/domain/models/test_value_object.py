import pytest

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import AbstractValueObject


def test_value_object_equals() -> None:
    @immutable
    class SampleValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="John", age=30)
    assert value_object1 == value_object2


def test_value_object_not_equals() -> None:
    @immutable
    class SampleValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="Sarah", age=30)
    assert value_object1 != value_object2


def test_value_object_not_equals_with_wrong_type() -> None:
    @immutable
    class SampleValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    @immutable
    class AnotherValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: AnotherValueObject = AnotherValueObject(name="Sarah", age=30)
    assert value_object1 != value_object2


def test_value_object_clone() -> None:
    @immutable
    class SampleValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = value_object1.clone()
    assert value_object1 == value_object2


def test_value_object_hash() -> None:
    @immutable
    class SampleValueObject(AbstractValueObject):
        name: str
        age: int

        def validate(self) -> None:
            return

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="John", age=30)
    assert hash(value_object1) == hash(value_object2)


def test_value_object_can_only_composed_by_hashable_objects_expect_success() -> None:
    @immutable
    class _(AbstractValueObject):
        name: str
        age: int
        jobs: frozenset[str]

        def validate(self) -> None:
            return


def test_value_object_can_only_composed_by_hashable_objects_expect_error() -> None:
    with pytest.raises(TypeError, match="type of 'jobs' is not hashable"):

        @immutable
        class _(AbstractValueObject):
            name: str
            age: int
            jobs: list[str]

            def validate(self) -> None:
                return
