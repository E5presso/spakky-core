from abc import ABC, abstractmethod

from fastapi.testclient import TestClient
from spakky.framework import (
    ISpakkyBootApplication,
    SpakkyApplication,
    SpakkyBootApplication,
    ApplicationContext,
    Autowired,
    Component,
)


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


@Component()
class A(IA):
    def a(self) -> str:
        return "A"


@Component()
class B(IB):
    def b(self) -> str:
        return "B"


@Component()
class C(IC):
    __a: IA
    __b: IB

    @Autowired()
    def __init__(self, a: IA, b: IB) -> None:
        self.__a = a
        self.__b = b

    def c(self) -> str:
        return self.__a.a() + self.__b.b()


@SpakkyBootApplication()
class Program(ISpakkyBootApplication):
    __context__: ApplicationContext

    @classmethod
    def main(cls) -> SpakkyApplication:
        return SpakkyApplication(cls)


def test_application_inject_via_context() -> None:
    app: SpakkyApplication = Program.main()
    c: IC = app.context.retrieve(IC)
    assert c.c() == "AB"


def test_application_inject_via_constructor() -> None:
    app: SpakkyApplication = Program.main()
    c: C = C(
        a=app.context.retrieve(IA),
        b=app.context.retrieve(IB),
    )
    assert c.c() == "AB"


def test_application_controller() -> None:
    app: SpakkyApplication = Program.main()
    client: TestClient = TestClient(app=app)
    assert client.get("/test").json() == "test"
