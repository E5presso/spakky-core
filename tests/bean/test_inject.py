from abc import ABC, abstractmethod

from spakky.bean.application_context import ApplicationContext
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.bean.inject import inject


def test_inject_to_function_by_type() -> None:
    class IA(ABC):
        @abstractmethod
        def a(self) -> str:
            ...

    class IB(ABC):
        @abstractmethod
        def b(self) -> str:
            ...

    class IC(ABC):
        @abstractmethod
        def c(self) -> str:
            ...

    @Bean()
    class A(IA):
        def a(self) -> str:
            return "a"

    @Bean()
    class B(IB):
        def b(self) -> str:
            return "b"

    @Bean()
    class C(IC):
        __a: IA
        __b: IB

        @autowired
        def __init__(self, a: IA, b: IB) -> None:
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(A)
    context.register_bean(B)
    context.register_bean(C)

    def execute_c(c: IC = inject(context=context, required_type=IC)) -> str:
        return c.c()

    assert execute_c() == "ab"


def test_inject_to_function_by_name() -> None:
    class IA(ABC):
        @abstractmethod
        def a(self) -> str:
            ...

    class IB(ABC):
        @abstractmethod
        def b(self) -> str:
            ...

    class IC(ABC):
        @abstractmethod
        def c(self) -> str:
            ...

    @Bean()
    class A(IA):
        def a(self) -> str:
            return "a"

    @Bean()
    class B(IB):
        def b(self) -> str:
            return "b"

    @Bean()
    class C(IC):
        __a: IA
        __b: IB

        @autowired
        def __init__(self, a, b) -> None:  # type: ignore
            self.__a = a
            self.__b = b

        def c(self) -> str:
            return self.__a.a() + self.__b.b()

    context: ApplicationContext = ApplicationContext()
    context.register_bean(A)
    context.register_bean(B)
    context.register_bean(C)

    def execute_c(c: IC = inject(context, IC, "c")) -> str:  # type: ignore
        return c.c()

    assert execute_c() == "ab"