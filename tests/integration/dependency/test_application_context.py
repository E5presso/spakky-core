from abc import ABC, abstractmethod
from uuid import UUID, uuid4
from typing import Callable
from dataclasses import dataclass

import pytest

from spakky.core.annotation import ClassAnnotation
from spakky.dependency.application_context import (
    ApplicationContext,
    CannotRegisterNonComponentError,
    NoSuchComponentError,
    NoUniqueComponentError,
)
from spakky.dependency.autowired import autowired
from spakky.dependency.component import Component
from spakky.dependency.primary import Primary
from spakky.dependency.provider import Provider, ProvidingType
from tests.integration import dummy_package
from tests.integration.dummy_package.module_a import ComponentA, DummyA
from tests.integration.dummy_package.module_b import ComponentB, DummyB
from tests.integration.dummy_package.module_c import ComponentC, DummyC


def test_application_context_register_expect_success() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)
    context.register_component(SecondSampleComponent)


def test_application_context_register_expect_error() -> None:
    class NonComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonComponentError):
        context.register_component(NonComponent)


def test_application_context_get_by_type_singleton_expect_success() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)
    context.register_component(SecondSampleComponent)

    assert (
        context.get(required_type=FirstSampleComponent).id
        == context.get(required_type=FirstSampleComponent).id
    )
    assert (
        context.get(required_type=SecondSampleComponent).id
        == context.get(required_type=SecondSampleComponent).id
    )


def test_application_context_get_by_type_expect_no_such_error() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)

    assert (
        context.get(required_type=FirstSampleComponent).id
        == context.get(required_type=FirstSampleComponent).id
    )
    with pytest.raises(NoSuchComponentError):
        assert (
            context.get(required_type=SecondSampleComponent).id
            == context.get(required_type=SecondSampleComponent).id
        )


def test_application_context_get_by_type_factory_expect_success() -> None:
    @Component()
    @Provider(ProvidingType.FACTORY)
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(SampleComponent)

    assert (
        context.get(required_type=SampleComponent).id
        != context.get(required_type=SampleComponent).id
    )


def test_application_context_get_by_name_expect_success() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(SampleComponent)

    assert isinstance(context.get(name="sample_component"), SampleComponent)


def test_application_context_get_by_name_expect_no_such_error() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(SampleComponent)

    with pytest.raises(NoSuchComponentError):
        context.get(name="wrong_component")


def test_application_context_contains_by_type_expect_true() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(SampleComponent)

    assert context.contains(required_type=SampleComponent) is True


def test_application_context_contains_by_type_expect_false() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)

    assert context.contains(required_type=FirstSampleComponent) is True
    assert context.contains(required_type=SecondSampleComponent) is False


def test_application_context_contains_by_name_expect_true() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True


def test_application_context_contains_by_name_expect_false() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True
    assert context.contains(name="wrong_sample_component") is False


def test_application_context_get_primary_expect_success() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)
    context.register_component(SecondSampleComponent)

    assert isinstance(context.get(required_type=ISampleComponent), FirstSampleComponent)


def test_application_context_get_primary_expect_no_unique_error() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleComponent)
    context.register_component(SecondSampleComponent)

    with pytest.raises(NoUniqueComponentError):
        context.get(required_type=ISampleComponent)


def test_application_context_get_dependency_recursive_by_name() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(A)
    context.register_component(B)
    context.register_component(C)

    assert context.get(required_type=C).c() == "ab"


def test_application_context_get_dependency_recursive_by_type() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(A)
    context.register_component(B)
    context.register_component(C)

    assert context.get(required_type=C).c() == "ab"


def test_application_context_where() -> None:
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

    context: ApplicationContext = ApplicationContext()
    context.register_component(FirstSampleClassMarked)
    context.register_component(SecondSampleClass)
    context.register_component(ThirdSampleClassMarked)

    queried: list[object] = list(context.where(lambda x: x.__name__.endswith("Marked")))
    assert isinstance(queried[0], FirstSampleClassMarked)
    assert isinstance(queried[1], ThirdSampleClassMarked)

    queried = list(context.where(Customized.contains))
    assert isinstance(queried[0], SecondSampleClass)
    assert isinstance(queried[1], ThirdSampleClassMarked)


def test_application_context_scan() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package)

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=ComponentB) is True
    assert context.contains(required_type=ComponentC) is True
    assert context.contains(required_type=DummyA) is False
    assert context.contains(required_type=DummyB) is False
    assert context.contains(required_type=DummyC) is False


def test_application_context_initialize_with_pacakge() -> None:
    context: ApplicationContext = ApplicationContext(package=dummy_package)

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=ComponentB) is True
    assert context.contains(required_type=ComponentC) is True
    assert context.contains(required_type=DummyA) is False
    assert context.contains(required_type=DummyB) is False
    assert context.contains(required_type=DummyC) is False


def test_application_context_register_unmanaged_factory() -> None:
    class A:
        def a(self) -> str:
            return "A"

    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    context.register_unmanaged_dependency("a", get_a)

    assert context.contains(name="a") is True
    factory: Callable[[], A] = context.get(name="a")
    assert isinstance(factory(), A)
    assert factory().a() == "A"


def test_application_context_register_unmanaged_dependency() -> None:
    class A:
        def a(self) -> str:
            return "A"

    context: ApplicationContext = ApplicationContext()
    context.register_unmanaged_dependency("a", A())

    assert context.contains(name="a") is True
    assert context.get(name="a").a() == "A"
