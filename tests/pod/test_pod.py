from abc import abstractmethod
from typing import Any, TypeVar, Protocol, cast

import pytest

from spakky.pod.pod import (
    CannotDeterminePodTypeError,
    CannotUseVarArgsInPodError,
    Dependency,
    Pod,
    is_class_pod,
    is_function_pod,
)


def test_pod_issubclass_of() -> None:
    class A: ...

    @Pod()
    class B(A): ...

    @Pod()
    class C(A): ...

    assert Pod.get(B).is_family_with(A) is True
    assert Pod.get(C).is_family_with(A) is True


def test_pod_issubclass_of_with_generic() -> None:
    T_contra = TypeVar("T_contra", contravariant=True)

    class IA(Protocol[T_contra]):
        @abstractmethod
        def do(self, t: T_contra) -> None: ...

    @Pod()
    class B(IA[int]):
        def do(self, t: int) -> None:
            return

    @Pod()
    class C(IA[str]):
        def do(self, t: str) -> None:
            return

    assert Pod.get(B).is_family_with(IA) is False
    assert Pod.get(C).is_family_with(IA) is False
    assert Pod.get(B).is_family_with(IA[int]) is True
    assert Pod.get(C).is_family_with(IA[str]) is True


def test_pod_instantiate() -> None:
    @Pod()
    class A:
        def __init__(self, a: int) -> None:
            self.a = a

    a: A = cast(A, Pod.get(A).instantiate({"a": 1}))
    assert a.a == 1


def test_pod_instantiate_with_default_value() -> None:
    @Pod()
    class A:
        def __init__(self, name: str, age: int = 30) -> None:
            self.name = name
            self.age = age

    a1: A = cast(A, Pod.get(A).instantiate({"name": "John"}))
    assert a1.name == "John"
    assert a1.age == 30

    a2: A = cast(A, Pod.get(A).instantiate({"name": "John", "age": 40}))
    assert a2.name == "John"
    assert a2.age == 40

    a3: A = cast(A, Pod.get(A).instantiate({"name": "John", "age": None}))
    assert a3.name == "John"
    assert a3.age == 30


def test_is_class_pod() -> None:
    class A: ...

    def a() -> None: ...

    assert is_class_pod(A) is True
    assert is_class_pod(a) is False


def test_is_function_pod() -> None:
    class A: ...

    def a() -> None: ...

    assert is_function_pod(A) is False
    assert is_function_pod(a) is True


def test_pod() -> None:
    @Pod()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Pod.get(SampleClass).dependencies == {
        "name": Dependency(type_=str, has_default=False, is_optional=False),
        "age": Dependency(type_=int, has_default=False, is_optional=False),
    }
    assert Pod.get(SampleClass).name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_pod_with_var_args() -> None:
    with pytest.raises(CannotUseVarArgsInPodError):

        @Pod()
        class _:
            name: str
            age: int

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.name = args[0] or kwargs["name"]
                self.age = args[1] or kwargs["age"]


def test_pod_factory_with_var_args() -> None:
    with pytest.raises(CannotUseVarArgsInPodError):

        @Pod()
        def _(*args: Any, **kwargs: Any) -> Any:
            return args[0] or kwargs["name"]


def test_pod_factory_with_return_annotation() -> None:
    class A: ...

    @Pod()
    def get_a() -> A:
        return A()

    assert Pod.exists(get_a) is True
    assert Pod.get(get_a) is not None
    assert Pod.get(get_a).name == "get_a"
    assert Pod.get(get_a).type_ is A


def test_pod_factory_without_return_annotation() -> None:
    class A: ...

    with pytest.raises(CannotDeterminePodTypeError):

        @Pod()
        def _():
            return A()


def test_pod_with_scope() -> None:
    @Pod(scope=Pod.Scope.PROTOTYPE)
    class A: ...

    assert Pod.exists(A) is True
    assert Pod.get(A) is not None
    assert Pod.get(A).scope is Pod.Scope.PROTOTYPE


def test_pod_factory_with_scope() -> None:
    class A: ...

    @Pod(scope=Pod.Scope.PROTOTYPE)
    def get_a() -> A:
        return A()

    assert Pod.exists(get_a) is True
    assert Pod.get(get_a) is not None
    assert Pod.get(get_a).name == "get_a"
    assert Pod.get(get_a).type_ is A
    assert Pod.get(get_a).scope is Pod.Scope.PROTOTYPE


def test_pod_with_name() -> None:
    @Pod(name="asdf")
    class A: ...

    assert Pod.exists(A) is True
    assert Pod.get(A) is not None
    assert Pod.get(A).name == "asdf"


def test_pod_factory_with_name() -> None:
    class A: ...

    @Pod(name="a")
    def get_a() -> A:
        return A()

    assert Pod.exists(get_a) is True
    assert Pod.get(get_a) is not None
    assert Pod.get(get_a).name == "a"
    assert Pod.get(get_a).type_ is A
