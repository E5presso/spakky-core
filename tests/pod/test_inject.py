from abc import abstractmethod
from typing import Protocol

from spakky.application.application_context import ApplicationContext
from spakky.pod.annotations.pod import Pod
from spakky.pod.inject import inject


def test_inject_to_function_by_type() -> None:
    class IA(Protocol):
        @abstractmethod
        def a(self) -> str: ...

    class IB(Protocol):
        @abstractmethod
        def b(self) -> str: ...

    class IC(Protocol):
        @abstractmethod
        def c(self) -> str: ...

    @Pod()
    class A(IA):
        def a(self) -> str:
            return "a"

    @Pod()
    class B(IB):
        def b(self) -> str:
            return "b"

    @Pod()
    class C(IC):
        __a: IA
        __b: IB

        def __init__(self, a: IA, b: IB) -> None:
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.add(A)
    context.add(B)
    context.add(C)

    def execute_c(c: IC = inject(context, type_=IC)) -> str:
        return c.c()

    assert execute_c() == "ab"
