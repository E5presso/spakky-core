import inspect
from uuid import UUID, uuid4
from dataclasses import dataclass

import pytest

from spakky.core.annotation import (
    Annotation,
    AnnotationNotFoundError,
    ClassAnnotation,
    FunctionAnnotation,
    MultipleAnnotationFoundError,
)


def test_class_annotation_expect_success() -> None:
    @ClassAnnotation()
    class Dummy: ...

    assert ClassAnnotation.contains(Dummy)
    assert ClassAnnotation.single_or_none(Dummy) is not None
    assert ClassAnnotation.single_or_default(Dummy, ClassAnnotation()) is not None
    assert ClassAnnotation.single(Dummy)


def test_class_annotation_expect_fail() -> None:
    class Dummy: ...

    with pytest.raises(AssertionError):
        assert ClassAnnotation.contains(Dummy)
    with pytest.raises(AssertionError):
        assert ClassAnnotation.single_or_none(Dummy) is not None
    with pytest.raises(AnnotationNotFoundError):
        ClassAnnotation.single(Dummy)


def test_multiple_class_annotation_expect_success() -> None:
    @dataclass
    class DummyAnnotation(ClassAnnotation): ...

    @dataclass
    class AnotherAnnotation(ClassAnnotation): ...

    @DummyAnnotation()
    @AnotherAnnotation()
    class Dummy: ...

    assert DummyAnnotation.contains(Dummy)
    assert AnotherAnnotation.contains(Dummy)


def test_same_class_annotation_multiple_times_expect_error() -> None:
    @dataclass
    class DummyAnnotation(ClassAnnotation):
        age: int

    @DummyAnnotation(age=29)
    @DummyAnnotation(age=30)
    class Dummy: ...

    with pytest.raises(MultipleAnnotationFoundError):
        DummyAnnotation.single(Dummy)
    with pytest.raises(MultipleAnnotationFoundError):
        DummyAnnotation.single_or_none(Dummy)
    with pytest.raises(MultipleAnnotationFoundError):
        DummyAnnotation.single_or_default(Dummy, DummyAnnotation(age=30))

    assert DummyAnnotation.all(Dummy) == [
        DummyAnnotation(age=30),
        DummyAnnotation(age=29),
    ]


def test_function_passing_type_hint() -> None:
    @dataclass
    class CustomAnnotation(FunctionAnnotation): ...

    def func(name: str, age: int) -> tuple[str, int]:
        return name, age

    old_signature: inspect.Signature = inspect.signature(func)

    func = CustomAnnotation()(func)

    assert inspect.signature(func) == old_signature
    assert func(name="John", age=30) == ("John", 30)


def test_function_annotation_expect_success() -> None:
    @FunctionAnnotation()
    def function() -> None: ...

    assert FunctionAnnotation.contains(function)
    assert FunctionAnnotation.single_or_none(function) is not None
    assert FunctionAnnotation.single(function)

    @dataclass
    class CustomAnnotation(Annotation):
        name: str
        age: int

    @CustomAnnotation(name="John", age=30)
    @CustomAnnotation(name="Sarah", age=28)
    def sample() -> None: ...

    annotations: list[CustomAnnotation] = CustomAnnotation.all(sample)
    assert annotations == [
        CustomAnnotation(name="Sarah", age=28),
        CustomAnnotation(name="John", age=30),
    ]


def test_function_annotation_expect_fail() -> None:
    def function() -> None: ...

    with pytest.raises(AssertionError):
        assert FunctionAnnotation.contains(function)
    with pytest.raises(AssertionError):
        assert FunctionAnnotation.single_or_none(function) is not None
    with pytest.raises(AnnotationNotFoundError):
        FunctionAnnotation.single(function)


def test_multiple_function_annotation_expect_success() -> None:
    @dataclass
    class DummyAnnotation(FunctionAnnotation): ...

    @dataclass
    class AnotherAnnotation(FunctionAnnotation): ...

    @DummyAnnotation()
    @AnotherAnnotation()
    def function() -> None: ...

    assert DummyAnnotation.contains(function)
    assert AnotherAnnotation.contains(function)


def test_same_function_annotation_multiple_times_expect_error() -> None:
    @dataclass
    class DummyAnnotation(FunctionAnnotation):
        name: str

    @DummyAnnotation(name="John")
    @DummyAnnotation(name="Sarah")
    def dummy() -> None: ...

    with pytest.raises(MultipleAnnotationFoundError):
        DummyAnnotation.single(dummy)
    with pytest.raises(MultipleAnnotationFoundError):
        DummyAnnotation.single_or_none(dummy)

    assert DummyAnnotation.all(dummy) == [
        DummyAnnotation(name="Sarah"),
        DummyAnnotation(name="John"),
    ]


def test_class_annotation_inheritance() -> None:
    uid: UUID = uuid4()

    @dataclass(kw_only=True)
    class Foo(ClassAnnotation):
        uid: UUID

    @dataclass(kw_only=True)
    class Bar(Foo):
        name: str

    @dataclass(kw_only=True)
    class Baz(Bar): ...

    @Baz(uid=uid, name="John")
    class Dummy: ...

    assert Baz.contains(Dummy)
    assert Bar.contains(Dummy)
    assert Foo.contains(Dummy)

    assert Baz.single(Dummy).uid == uid
    assert Baz.single(Dummy).name == "John"
    assert Bar.single(Dummy).uid == uid
    assert Bar.single(Dummy).name == "John"
    assert Foo.single(Dummy).uid == uid


def test_class_annotation_inheritance_expect_fail() -> None:
    @dataclass(kw_only=True)
    class Foo(ClassAnnotation):
        uid: UUID

    @dataclass(kw_only=True)
    class Bar(Foo):
        name: str

    @dataclass(kw_only=True)
    class Baz(Bar): ...

    @Bar(uid=uuid4(), name="John")
    class Dummy2: ...

    assert Bar.contains(Dummy2)
    assert Foo.contains(Dummy2)
    with pytest.raises(AssertionError):
        assert Baz.contains(Dummy2)
