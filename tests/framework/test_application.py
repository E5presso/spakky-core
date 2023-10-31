from abc import ABC, abstractmethod
from threading import Event as ThreadEvent
import time

from fastapi.testclient import TestClient
from spakky.framework import (
    SpakkyApplication,
    SpakkyBootApplication,
    ApplicationContext,
    Autowired,
    Component,
    Controller,
)
from spakky.framework.context.stereotype.task import ISyncTask, SyncTask
from spakky.framework.web import get


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


@Controller("/test")
class ForTestController:
    __c: IC

    @Autowired()
    def __init__(self, c: IC) -> None:
        self.__c = c

    @get("")
    async def get_test(self) -> str:
        return self.__c.c()


@SyncTask()
class ForTestTask(ISyncTask):
    __c: IC

    @Autowired()
    def __init__(self, c: IC) -> None:
        self.__c = c

    def start(self, signal: ThreadEvent) -> None:
        while not signal.is_set():
            print(f"Sync Loop is still running! {self.__c.c()}")
            time.sleep(0.1)
        print("Sync Loop is done!")


@SpakkyBootApplication()
class Program:
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
    assert client.get("/test").json() == "AB"


def test_application_task() -> None:
    app: SpakkyApplication = Program.main()
    with TestClient(app=app, base_url="http://test") as _:
        time.sleep(1)
