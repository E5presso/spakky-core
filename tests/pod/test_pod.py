from typing import Any

import pytest

from spakky.pod.pod import CannotDeterminePodTypeError, CannotUseVarArgsInPodError, Pod


def test_pod() -> None:
    @Pod()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Pod.get(SampleClass).dependencies == {"name": str, "age": int}
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
