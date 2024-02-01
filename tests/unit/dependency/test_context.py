from abc import ABC, abstractmethod
from uuid import UUID, uuid4
from dataclasses import dataclass

import pytest

from spakky.core.annotation import ClassAnnotation
from spakky.dependency.autowired import autowired
from spakky.dependency.component import Component
from spakky.dependency.context import (
    CannotRegisterNonComponentError,
    Context,
    NoSuchComponentError,
    NoUniqueComponentError,
)
from spakky.dependency.primary import Primary
from spakky.dependency.provider import Provider, ProvidingType


def test_context_register_expect_success() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Component()
    @Provider(ProvidingType.FACTORY)
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)
    context.register(SecondSampleComponent)


def test_context_register_expect_error() -> None:
    class NonComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    with pytest.raises(CannotRegisterNonComponentError):
        context.register(NonComponent)


def test_context_get_by_type_singleton_expect_success() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Component()
    @Provider(ProvidingType.SINGLETON)
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)
    context.register(SecondSampleComponent)

    assert (
        context.get(required_type=FirstSampleComponent).id
        == context.get(required_type=FirstSampleComponent).id
    )
    assert (
        context.get(required_type=SecondSampleComponent).id
        == context.get(required_type=SecondSampleComponent).id
    )


def test_context_get_by_type_expect_no_such_error() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)

    assert (
        context.get(required_type=FirstSampleComponent).id
        == context.get(required_type=FirstSampleComponent).id
    )
    with pytest.raises(NoSuchComponentError):
        assert (
            context.get(required_type=SecondSampleComponent).id
            == context.get(required_type=SecondSampleComponent).id
        )


def test_context_get_by_type_factory_expect_success() -> None:
    @Component()
    @Provider(ProvidingType.FACTORY)
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(SampleComponent)

    assert (
        context.get(required_type=SampleComponent).id
        != context.get(required_type=SampleComponent).id
    )


def test_context_get_by_name_expect_success() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(SampleComponent)

    assert isinstance(context.get(name="sample_component"), SampleComponent)


def test_context_get_by_name_expect_no_such_error() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(SampleComponent)

    with pytest.raises(NoSuchComponentError):
        context.get(name="wrong_component")


def test_context_contains_by_type_expect_true() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(SampleComponent)

    assert context.contains(required_type=SampleComponent) is True


def test_context_contains_by_type_expect_false() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Component()
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)

    assert context.contains(required_type=FirstSampleComponent) is True
    assert context.contains(required_type=SecondSampleComponent) is False


def test_context_contains_by_name_expect_true() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True


def test_context_contains_by_name_expect_false() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: Context = Context()
    context.register(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True
    assert context.contains(name="wrong_sample_component") is False


def test_context_get_primary_expect_success() -> None:
    class ISampleComponent(ABC):
        @abstractmethod
        def do(self) -> None:
            ...

    @Primary()
    @Component()
    class FirstSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    @Component()
    class SecondSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    context: Context = Context()
    context.register(FirstSampleComponent)
    context.register(SecondSampleComponent)

    assert isinstance(context.get(required_type=ISampleComponent), FirstSampleComponent)


def test_context_get_primary_expect_no_unique_error() -> None:
    class ISampleComponent(ABC):
        @abstractmethod
        def do(self) -> None:
            ...

    @Primary()
    @Component()
    class FirstSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    @Primary()
    @Component()
    class SecondSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    context: Context = Context()
    context.register(FirstSampleComponent)
    context.register(SecondSampleComponent)

    with pytest.raises(NoUniqueComponentError):
        context.get(required_type=ISampleComponent)


def test_context_get_dependency_recursive_by_name() -> None:
    @Component()
    class A:
        def a(self) -> str:
            return "a"

    @Component()
    class B:
        def b(self) -> str:
            return "b"

    @Component()
    class C:
        __a: A
        __b: B

        @autowired
        def __init__(self, a, b) -> None:  # type: ignore
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: Context = Context()
    context.register(A)
    context.register(B)
    context.register(C)

    assert context.get(required_type=C).c() == "ab"


def test_context_get_dependency_recursive_by_type() -> None:
    @Component()
    class A:
        def a(self) -> str:
            return "a"

    @Component()
    class B:
        def b(self) -> str:
            return "b"

    @Component()
    class C:
        __a: A
        __b: B

        @autowired
        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: Context = Context()
    context.register(A)
    context.register(B)
    context.register(C)

    assert context.get(required_type=C).c() == "ab"


def test_context_where() -> None:
    @dataclass
    class Customized(ClassAnnotation):
        ...

    @Component()
    class FirstSampleClassMarked:
        ...

    @Component()
    @Customized()
    class SecondSampleClass:
        ...

    @Component()
    @Customized()
    class ThirdSampleClassMarked:
        ...

    context: Context = Context()
    context.register(FirstSampleClassMarked)
    context.register(SecondSampleClass)
    context.register(ThirdSampleClassMarked)

    queried: list[object] = list(context.where(lambda x: x.__name__.endswith("Marked")))
    assert isinstance(queried[0], FirstSampleClassMarked)
    assert isinstance(queried[1], ThirdSampleClassMarked)

    queried = list(context.where(Customized.contains))
    assert isinstance(queried[0], SecondSampleClass)
    assert isinstance(queried[1], ThirdSampleClassMarked)
