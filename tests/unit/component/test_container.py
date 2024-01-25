from abc import ABC, abstractmethod
from uuid import UUID, uuid4
from dataclasses import dataclass

import pytest

from spakky.component.autowired import autowired
from spakky.component.component import Component
from spakky.component.container import (
    CannotRegisterNonComponentError,
    ComponentContainer,
    NoSuchComponentError,
    NoUniqueComponentError,
)
from spakky.component.primary import Primary
from spakky.component.provider import Provider, ProvidingType
from spakky.core.annotation import ClassAnnotation


def test_container_register_expect_success() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)
    container.register(SecondSampleComponent)


def test_container_register_expect_error() -> None:
    class NonComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    with pytest.raises(CannotRegisterNonComponentError):
        container.register(NonComponent)


def test_container_get_by_type_singleton_expect_success() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)
    container.register(SecondSampleComponent)

    assert (
        container.get(required_type=FirstSampleComponent).id
        == container.get(required_type=FirstSampleComponent).id
    )
    assert (
        container.get(required_type=SecondSampleComponent).id
        == container.get(required_type=SecondSampleComponent).id
    )


def test_container_get_by_type_expect_no_such_error() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    class SecondSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)

    assert (
        container.get(required_type=FirstSampleComponent).id
        == container.get(required_type=FirstSampleComponent).id
    )
    with pytest.raises(NoSuchComponentError):
        assert (
            container.get(required_type=SecondSampleComponent).id
            == container.get(required_type=SecondSampleComponent).id
        )


def test_container_get_by_type_factory_expect_success() -> None:
    @Component()
    @Provider(ProvidingType.FACTORY)
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(SampleComponent)

    assert (
        container.get(required_type=SampleComponent).id
        != container.get(required_type=SampleComponent).id
    )


def test_container_get_by_name_expect_success() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(SampleComponent)

    assert isinstance(container.get(name="sample_component"), SampleComponent)


def test_container_get_by_name_expect_no_such_error() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(SampleComponent)

    with pytest.raises(NoSuchComponentError):
        container.get(name="wrong_component")


def test_container_contains_by_type_expect_true() -> None:
    @Component()
    class SampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(SampleComponent)

    assert container.contains(required_type=SampleComponent) is True


def test_container_contains_by_type_expect_false() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)

    assert container.contains(required_type=FirstSampleComponent) is True
    assert container.contains(required_type=SecondSampleComponent) is False


def test_container_contains_by_name_expect_true() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)

    assert container.contains(name="first_sample_component") is True


def test_container_contains_by_name_expect_false() -> None:
    @Component()
    class FirstSampleComponent:
        id: UUID

        def __init__(self) -> None:
            self.id = uuid4()

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)

    assert container.contains(name="first_sample_component") is True
    assert container.contains(name="wrong_sample_component") is False


def test_container_get_primary_expect_success() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)
    container.register(SecondSampleComponent)

    assert isinstance(container.get(required_type=ISampleComponent), FirstSampleComponent)


def test_container_get_primary_expect_no_unique_error() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleComponent)
    container.register(SecondSampleComponent)

    with pytest.raises(NoUniqueComponentError):
        container.get(required_type=ISampleComponent)


def test_container_get_dependency_recursive_by_name() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(A)
    container.register(B)
    container.register(C)

    assert container.get(required_type=C).c() == "ab"


def test_container_get_dependency_recursive_by_type() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(A)
    container.register(B)
    container.register(C)

    assert container.get(required_type=C).c() == "ab"


def test_container_where() -> None:
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

    container: ComponentContainer = ComponentContainer()
    container.register(FirstSampleClassMarked)
    container.register(SecondSampleClass)
    container.register(ThirdSampleClassMarked)

    queried: list[object] = list(container.where(lambda x: x.__name__.endswith("Marked")))
    assert isinstance(queried[0], FirstSampleClassMarked)
    assert isinstance(queried[1], ThirdSampleClassMarked)

    queried = list(container.where(Customized.contains))
    assert isinstance(queried[0], SecondSampleClass)
    assert isinstance(queried[1], ThirdSampleClassMarked)
