from spakky.domain.models.value_object import ValueObject
from spakky.core.mutability import immutable


def test_value_object_equals() -> None:
    @immutable
    class SampleValueObject(ValueObject):
        name: str
        age: int

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="John", age=30)
    assert value_object1 == value_object2


def test_value_object_not_equals() -> None:
    @immutable
    class SampleValueObject(ValueObject):
        name: str
        age: int

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="Sarah", age=30)
    assert value_object1 != value_object2


def test_value_object_not_equals_with_wrong_type() -> None:
    @immutable
    class SampleValueObject(ValueObject):
        name: str
        age: int

    @immutable
    class AnotherValueObject(ValueObject):
        name: str
        age: int

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: AnotherValueObject = AnotherValueObject(name="Sarah", age=30)
    assert value_object1 != value_object2


def test_value_object_clone() -> None:
    @immutable
    class SampleValueObject(ValueObject):
        name: str
        age: int

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = value_object1.clone()
    assert value_object1 == value_object2


def test_value_object_hash() -> None:
    @immutable
    class SampleValueObject(ValueObject):
        name: str
        age: int

    value_object1: SampleValueObject = SampleValueObject(name="John", age=30)
    value_object2: SampleValueObject = SampleValueObject(name="John", age=30)
    assert hash(value_object1) == hash(value_object2)
