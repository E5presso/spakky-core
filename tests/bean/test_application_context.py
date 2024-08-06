from abc import abstractmethod
from uuid import UUID, uuid4
from typing import Protocol
from dataclasses import dataclass

import pytest

from spakky.bean.application_context import (
    ApplicationContext,
    CannotRegisterNonBeanObjectError,
    NoSuchBeanError,
    NoUniqueBeanError,
)
from spakky.bean.bean import Bean
from spakky.bean.primary import Primary
from spakky.core.annotation import ClassAnnotation
from tests import dummy_package, second_dummy_package
from tests.dummy_package import module_a
from tests.dummy_package.module_a import ComponentA, DummyA
from tests.dummy_package.module_b import ComponentB, DummyB, UnmanagedB
from tests.dummy_package.module_c import ComponentC, DummyC
from tests.second_dummy_package import second_module_a
from tests.second_dummy_package.second_module_a import SecondComponentA, SecondDummyA
from tests.second_dummy_package.second_module_b import SecondComponentB, SecondDummyB
from tests.second_dummy_package.second_module_c import SecondComponentC, SecondDummyC


def test_application_context_register_expect_success() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Bean()
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)
    context.register_bean(SecondSampleComponent)


def test_application_context_register_expect_error() -> None:
    class NonComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonBeanObjectError):
        context.register_bean(NonComponent)


def test_application_context_get_by_type_singleton_expect_success() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Bean()
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)
    context.register_bean(SecondSampleComponent)

    assert (
        context.single(required_type=FirstSampleComponent).id
        == context.single(required_type=FirstSampleComponent).id
    )
    assert (
        context.single(required_type=SecondSampleComponent).id
        == context.single(required_type=SecondSampleComponent).id
    )


def test_application_context_get_by_type_expect_no_such_error() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)

    assert (
        context.single(required_type=FirstSampleComponent).id
        == context.single(required_type=FirstSampleComponent).id
    )
    with pytest.raises(NoSuchBeanError):
        assert (
            context.single(required_type=SecondSampleComponent).id
            == context.single(required_type=SecondSampleComponent).id
        )


def test_application_context_get_by_name_expect_success() -> None:
    @Bean()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(SampleComponent)

    assert isinstance(context.single(name="sample_component"), SampleComponent)


def test_application_context_get_by_name_expect_no_such_error() -> None:
    @Bean()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(SampleComponent)

    with pytest.raises(NoSuchBeanError):
        context.single(name="wrong_component")


def test_application_context_contains_by_type_expect_true() -> None:
    @Bean()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(SampleComponent)

    assert context.contains(required_type=SampleComponent) is True


def test_application_context_contains_by_type_expect_false() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Bean()
    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)

    assert context.contains(required_type=FirstSampleComponent) is True
    assert context.contains(required_type=SecondSampleComponent) is False


def test_application_context_contains_by_name_expect_true() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True


def test_application_context_contains_by_name_expect_false() -> None:
    @Bean()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)

    assert context.contains(name="first_sample_component") is True
    assert context.contains(name="wrong_sample_component") is False


def test_application_context_get_primary_expect_success() -> None:
    class ISampleComponent(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Bean()
    class FirstSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    @Bean()
    class SecondSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)
    context.register_bean(SecondSampleComponent)

    assert isinstance(
        context.single(required_type=ISampleComponent), FirstSampleComponent
    )


def test_application_context_get_primary_expect_no_unique_error() -> None:
    class ISampleComponent(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Bean()
    class FirstSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    @Primary()
    @Bean()
    class SecondSampleComponent(ISampleComponent):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleComponent)
    context.register_bean(SecondSampleComponent)

    with pytest.raises(NoUniqueBeanError):
        context.single(required_type=ISampleComponent)


def test_application_context_get_dependency_recursive_by_name() -> None:
    @Bean()
    class A:
        def a(self) -> str:
            return "a"

    @Bean()
    class B:
        def b(self) -> str:
            return "b"

    @Bean()
    class C:
        __a: A
        __b: B

        def __init__(self, a, b) -> None:  # type: ignore
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(A)
    context.register_bean(B)
    context.register_bean(C)

    assert context.single(required_type=C).c() == "ab"


def test_application_context_get_dependency_recursive_by_type() -> None:
    @Bean()
    class A:
        def a(self) -> str:
            return "a"

    @Bean()
    class B:
        def b(self) -> str:
            return "b"

    @Bean()
    class C:
        __a: A
        __b: B

        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(A)
    context.register_bean(B)
    context.register_bean(C)

    assert context.single(required_type=C).c() == "ab"


def test_application_context_where() -> None:
    @dataclass
    class Customized(ClassAnnotation): ...

    @Bean()
    class FirstSampleClassMarked: ...

    @Bean()
    @Customized()
    class SecondSampleClass: ...

    @Bean()
    @Customized()
    class ThirdSampleClassMarked: ...

    context: ApplicationContext = ApplicationContext()
    context.register_bean(FirstSampleClassMarked)
    context.register_bean(SecondSampleClass)
    context.register_bean(ThirdSampleClassMarked)

    queried: list[object] = list(
        context.filter_beans(lambda x: x.__name__.endswith("Marked"))
    )
    assert isinstance(queried[0], FirstSampleClassMarked)
    assert isinstance(queried[1], ThirdSampleClassMarked)

    queried = list(context.filter_beans(Customized.contains))
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
    assert context.contains(required_type=UnmanagedB) is True
    assert context.contains(name="unmanaged_b") is True


def test_application_context_initialize_with_pacakge() -> None:
    context: ApplicationContext = ApplicationContext(package=dummy_package)

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=ComponentB) is True
    assert context.contains(required_type=ComponentC) is True
    assert context.contains(required_type=DummyA) is False
    assert context.contains(required_type=DummyB) is False
    assert context.contains(required_type=DummyC) is False


def test_application_context_initialize_with_module() -> None:
    context: ApplicationContext = ApplicationContext(package=module_a)

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=DummyA) is False


def test_application_context_initialize_with_multiple_pacakges() -> None:
    context: ApplicationContext = ApplicationContext(
        package=[
            dummy_package,
            second_dummy_package,
        ]
    )

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=ComponentB) is True
    assert context.contains(required_type=ComponentC) is True
    assert context.contains(required_type=DummyA) is False
    assert context.contains(required_type=DummyB) is False
    assert context.contains(required_type=DummyC) is False

    assert context.contains(required_type=SecondComponentA) is True
    assert context.contains(required_type=SecondComponentB) is True
    assert context.contains(required_type=SecondComponentC) is True
    assert context.contains(required_type=SecondDummyA) is False
    assert context.contains(required_type=SecondDummyB) is False
    assert context.contains(required_type=SecondDummyC) is False


def test_application_context_initialize_with_multiple_pacakges_and_modules() -> None:
    context: ApplicationContext = ApplicationContext(
        package=[
            dummy_package,
            second_module_a,
        ]
    )

    assert context.contains(required_type=ComponentA) is True
    assert context.contains(required_type=ComponentB) is True
    assert context.contains(required_type=ComponentC) is True

    assert context.contains(required_type=SecondComponentA) is True


def test_application_context_register_unmanaged_factory() -> None:
    class A:
        def a(self) -> str:
            return "A"

    @Bean()
    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    context.register_bean_factory(get_a)

    assert context.contains(name="get_a") is True
    a: A = context.single(name="get_a")
    assert isinstance(a, A)
    assert a.a() == "A"


def test_application_context_register_unmanaged_factory_expect_error() -> None:
    class A:
        def a(self) -> str:
            return "A"

    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonBeanObjectError):
        context.register_bean_factory(get_a)
