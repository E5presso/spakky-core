from abc import abstractmethod
from uuid import UUID, uuid4
from typing import Protocol
from dataclasses import dataclass

import pytest

from spakky.application.application_context import (
    ApplicationContext,
    CannotRegisterNonInjectableObjectError,
    NoSuchInjectableError,
    NoUniqueInjectableError,
)
from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry
from spakky.core.annotation import ClassAnnotation
from spakky.injectable.injectable import Injectable
from spakky.injectable.primary import Primary
from tests.dummy import dummy_package, second_dummy_package
from tests.dummy.dummy_package import module_a
from tests.dummy.dummy_package.module_a import DummyA, InjectableA
from tests.dummy.dummy_package.module_b import DummyB, InjectableB, UnmanagedB
from tests.dummy.dummy_package.module_c import DummyC, InjectableC
from tests.dummy.second_dummy_package import second_module_a
from tests.dummy.second_dummy_package.second_module_a import (
    SecondDummyA,
    SecondInjectableA,
)
from tests.dummy.second_dummy_package.second_module_b import (
    SecondDummyB,
    SecondInjectableB,
)
from tests.dummy.second_dummy_package.second_module_c import (
    SecondDummyC,
    SecondInjectableC,
)


def test_application_context_register_expect_success() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Injectable()
    class SecondSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)
    context.register_injectable(SecondSampleInjectable)


def test_application_context_register_expect_error() -> None:
    class NonInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonInjectableObjectError):
        context.register_injectable(NonInjectable)


def test_application_context_get_by_type_singleton_expect_success() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Injectable()
    class SecondSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)
    context.register_injectable(SecondSampleInjectable)

    assert (
        context.get(type_=FirstSampleInjectable).id
        == context.get(type_=FirstSampleInjectable).id
    )
    assert (
        context.get(type_=SecondSampleInjectable).id
        == context.get(type_=SecondSampleInjectable).id
    )


def test_application_context_get_by_type_expect_no_such_error() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)

    assert (
        context.get(type_=FirstSampleInjectable).id
        == context.get(type_=FirstSampleInjectable).id
    )
    with pytest.raises(NoSuchInjectableError):
        assert (
            context.get(type_=SecondSampleInjectable).id
            == context.get(type_=SecondSampleInjectable).id
        )


def test_application_context_get_by_name_expect_success() -> None:
    @Injectable()
    class SampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(SampleInjectable)

    assert isinstance(context.get(name="sample_injectable"), SampleInjectable)


def test_application_context_get_by_name_expect_no_such_error() -> None:
    @Injectable()
    class SampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(SampleInjectable)

    with pytest.raises(NoSuchInjectableError):
        context.get(name="wrong_injectable")


def test_application_context_contains_by_type_expect_true() -> None:
    @Injectable()
    class SampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(SampleInjectable)

    assert context.contains(type_=SampleInjectable) is True


def test_application_context_contains_by_type_expect_false() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    @Injectable()
    class SecondSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)

    assert context.contains(type_=FirstSampleInjectable) is True
    assert context.contains(type_=SecondSampleInjectable) is False


def test_application_context_contains_by_name_expect_true() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)

    assert context.contains(name="first_sample_injectable") is True


def test_application_context_contains_by_name_expect_false() -> None:
    @Injectable()
    class FirstSampleInjectable:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)

    assert context.contains(name="first_sample_injectable") is True
    assert context.contains(name="wrong_sample_injectable") is False


def test_application_context_get_primary_expect_success() -> None:
    class ISampleInjectable(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Injectable()
    class FirstSampleInjectable(ISampleInjectable):
        def do(self) -> None:
            return

    @Injectable()
    class SecondSampleInjectable(ISampleInjectable):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)
    context.register_injectable(SecondSampleInjectable)

    assert isinstance(context.get(type_=ISampleInjectable), FirstSampleInjectable)


def test_application_context_get_primary_expect_no_unique_error() -> None:
    class ISampleInjectable(Protocol):
        @abstractmethod
        def do(self) -> None: ...

    @Primary()
    @Injectable()
    class FirstSampleInjectable(ISampleInjectable):
        def do(self) -> None:
            return

    @Primary()
    @Injectable()
    class SecondSampleInjectable(ISampleInjectable):
        def do(self) -> None:
            return

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleInjectable)
    context.register_injectable(SecondSampleInjectable)

    with pytest.raises(NoUniqueInjectableError):
        context.get(type_=ISampleInjectable)


def test_application_context_get_dependency_recursive_by_name() -> None:
    @Injectable()
    class A:
        def a(self) -> str:
            return "a"

    @Injectable()
    class B:
        def b(self) -> str:
            return "b"

    @Injectable()
    class C:
        __a: A
        __b: B

        def __init__(self, a, b) -> None:  # type: ignore
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(A)
    context.register_injectable(B)
    context.register_injectable(C)

    assert context.get(type_=C).c() == "ab"


def test_application_context_get_dependency_recursive_by_type() -> None:
    @Injectable()
    class A:
        def a(self) -> str:
            return "a"

    @Injectable()
    class B:
        def b(self) -> str:
            return "b"

    @Injectable()
    class C:
        __a: A
        __b: B

        def __init__(self, b: A, a: B) -> None:
            self.__a = b
            self.__b = a

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(A)
    context.register_injectable(B)
    context.register_injectable(C)

    assert context.get(type_=C).c() == "ab"


def test_application_context_where() -> None:
    @dataclass
    class Customized(ClassAnnotation): ...

    @Injectable()
    class FirstSampleClassMarked: ...

    @Injectable()
    @Customized()
    class SecondSampleClass: ...

    @Injectable()
    @Customized()
    class ThirdSampleClassMarked: ...

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(FirstSampleClassMarked)
    context.register_injectable(SecondSampleClass)
    context.register_injectable(ThirdSampleClassMarked)

    queried: list[object] = list(
        context.filter_injectables(lambda x: x.__name__.endswith("Marked"))
    )
    assert isinstance(queried[0], FirstSampleClassMarked)
    assert isinstance(queried[1], ThirdSampleClassMarked)

    queried = list(context.filter_injectables(Customized.contains))
    assert isinstance(queried[0], SecondSampleClass)
    assert isinstance(queried[1], ThirdSampleClassMarked)


def test_application_context_scan() -> None:
    context: ApplicationContext = ApplicationContext()
    context.scan(dummy_package)

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=InjectableB) is True
    assert context.contains(type_=InjectableC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False
    assert context.contains(type_=UnmanagedB) is True
    assert context.contains(name="unmanaged_b") is True


def test_application_context_initialize_with_pacakge() -> None:
    context: ApplicationContext = ApplicationContext(package=dummy_package)

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=InjectableB) is True
    assert context.contains(type_=InjectableC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False


def test_application_context_initialize_with_module() -> None:
    context: ApplicationContext = ApplicationContext(package=module_a)

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=DummyA) is False


def test_application_context_initialize_with_multiple_pacakges() -> None:
    context: ApplicationContext = ApplicationContext(
        package={
            dummy_package,
            second_dummy_package,
        }
    )

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=InjectableB) is True
    assert context.contains(type_=InjectableC) is True
    assert context.contains(type_=DummyA) is False
    assert context.contains(type_=DummyB) is False
    assert context.contains(type_=DummyC) is False

    assert context.contains(type_=SecondInjectableA) is True
    assert context.contains(type_=SecondInjectableB) is True
    assert context.contains(type_=SecondInjectableC) is True
    assert context.contains(type_=SecondDummyA) is False
    assert context.contains(type_=SecondDummyB) is False
    assert context.contains(type_=SecondDummyC) is False


def test_application_context_initialize_with_multiple_pacakges_and_modules() -> None:
    context: ApplicationContext = ApplicationContext(
        package={
            dummy_package,
            second_module_a,
        }
    )

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=InjectableB) is True
    assert context.contains(type_=InjectableC) is True

    assert context.contains(type_=SecondInjectableA) is True


def test_application_context_register_unmanaged_factory() -> None:
    class A:
        def a(self) -> str:
            return "A"

    @Injectable()
    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    context.register_injectable(get_a)

    assert context.contains(name="get_a") is True
    a: A = context.get(name="get_a")
    assert isinstance(a, A)
    assert a.a() == "A"


def test_application_context_register_unmanaged_factory_expect_error() -> None:
    class A:
        def a(self) -> str:
            return "A"

    def get_a() -> A:
        return A()

    context: ApplicationContext = ApplicationContext()
    with pytest.raises(CannotRegisterNonInjectableObjectError):
        context.register_injectable(get_a)


def test_application_context_register_plugin() -> None:
    class DummyPlugin(IPluggable):
        def register(self, registry: IRegistry) -> None:
            registry.register_injectable(InjectableA)

    context: ApplicationContext = ApplicationContext()
    context.register_plugin(DummyPlugin())

    assert context.contains(type_=InjectableA) is True
    assert context.contains(type_=InjectableB) is False
