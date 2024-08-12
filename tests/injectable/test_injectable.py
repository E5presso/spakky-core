from typing import Any

import pytest

from spakky.injectable.injectable import (
    CannotDetermineInjectableTypeError,
    CannotUseVarArgsInInjectableError,
    Injectable,
)


def test_injectable() -> None:
    @Injectable()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Injectable.get(SampleClass).dependencies == {"name": str, "age": int}
    assert Injectable.get(SampleClass).name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_injectable_with_var_args() -> None:
    with pytest.raises(CannotUseVarArgsInInjectableError):

        @Injectable()
        class _:
            name: str
            age: int

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.name = args[0] or kwargs["name"]
                self.age = args[1] or kwargs["age"]


def test_injectable_factory_with_var_args() -> None:
    with pytest.raises(CannotUseVarArgsInInjectableError):

        @Injectable()
        def _(*args: Any, **kwargs: Any) -> Any:
            return args[0] or kwargs["name"]


def test_injectable_factory_with_return_annotation() -> None:
    class A: ...

    @Injectable()
    def get_a() -> A:
        return A()

    assert Injectable.contains(get_a) is True
    assert Injectable.get(get_a) is not None
    assert Injectable.get(get_a).name == "get_a"
    assert Injectable.get(get_a).type_ is A


def test_injectable_factory_without_return_annotation() -> None:
    class A: ...

    with pytest.raises(CannotDetermineInjectableTypeError):

        @Injectable()
        def _():
            return A()


def test_injectable_with_name() -> None:
    @Injectable(name="asdf")
    class A: ...

    assert Injectable.contains(A) is True
    assert Injectable.get(A) is not None
    assert Injectable.get(A).name == "asdf"


def test_injectable_factory_with_name() -> None:
    class A: ...

    @Injectable(name="a")
    def get_a() -> A:
        return A()

    assert Injectable.contains(get_a) is True
    assert Injectable.get(get_a) is not None
    assert Injectable.get(get_a).name == "a"
    assert Injectable.get(get_a).type_ is A
