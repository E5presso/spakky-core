from abc import ABC, abstractmethod

import pytest
from spakky.framework.context.application_context import (
    ApplicationContext,
    NoSuchComponentDefinitionException,
    NoUniqueComponentDefinitionException,
)

from spakky.framework.context.stereotype.component import Component


class IA(ABC):
    @abstractmethod
    def a(self) -> None:
        ...


class IB(ABC):
    @abstractmethod
    def b(self) -> None:
        ...


class IC(ABC):
    @abstractmethod
    def c(self) -> None:
        ...


class IW(ABC):
    @abstractmethod
    def w(self) -> None:
        ...


@Component()
class A(IA, IB):
    def a(self) -> None:
        print("A")

    def b(self) -> None:
        print("B")


@Component()
class B(IB, IC):
    def b(self) -> None:
        print("B")

    def c(self) -> None:
        print("C")


def test_register_and_retrieve_from_application_context() -> None:
    a_annotation: Component | None = Component.get_annotation(A)
    b_annotation: Component | None = Component.get_annotation(A)
    assert a_annotation is not None
    assert b_annotation is not None
    context: ApplicationContext = ApplicationContext()
    context.register(A)
    context.register(B)

    a: A = context.retrieve(A)
    ia: IA = context.retrieve(IA)
    ic: IC = context.retrieve(IC)

    with pytest.raises(NoUniqueComponentDefinitionException):
        ib: IB = context.retrieve(IB)
    with pytest.raises(NoSuchComponentDefinitionException):
        iw: IW = context.retrieve(IW)
    return
