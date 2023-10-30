from contextlib import asynccontextmanager
import dataclasses
from functools import partial
from typing import Any, AsyncGenerator, Protocol, Self, runtime_checkable
from asyncio import Event, Task, create_task
from threading import Thread, Event as ThreadEvent

from fastapi import APIRouter, Depends, FastAPI
from spakky.framework.context.application_context import ApplicationContext
from spakky.framework.context.component_scan import ComponentScan, IComponentScan
from spakky.framework.context.stereotype.controller import IController
from spakky.framework.core.generic import T_CLASS
from spakky.framework.daemon_task import IAsyncDaemonTask, IDaemonTask


@runtime_checkable
class ISpakkyBootApplication(IComponentScan, Protocol):
    def __instancecheck__(self, __instance: Any) -> bool:
        return super().__instancecheck__(__instance)

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return super().__subclasshook__(__subclass)


class SpakkyBootApplication(ComponentScan):
    def __call__(self, cls: T_CLASS) -> T_CLASS:
        return super().__call__(cls)


class SpakkyApplication(FastAPI):
    __context: ApplicationContext
    __controllers: list[type[IController]]
    __daemon_tasks: list[IDaemonTask | IAsyncDaemonTask]
    __running_tasks: list[Task[None] | Thread]
    __task_signal: Event
    __thread_signal: ThreadEvent

    @property
    def context(self) -> ApplicationContext:
        return self.__context

    def __init__(self, application: ISpakkyBootApplication, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__context = application.__context__
        self.__controllers = []
        self.__daemon_tasks = []
        self.__running_tasks = []
        self.__task_signal = Event()
        self.__thread_signal = ThreadEvent()
        self.__initialize_controllers()
        self.router.lifespan_context = self.__app_lifecycle_hook

    @asynccontextmanager
    async def __app_lifecycle_hook(self, _: Self) -> AsyncGenerator[None, None]:
        for daemon_task in self.__daemon_tasks:
            if isinstance(daemon_task, IDaemonTask):
                thread: Thread = Thread(target=daemon_task.start, args=(self.__thread_signal,))
                thread.start()
                self.__running_tasks.append(thread)
            if isinstance(daemon_task, IAsyncDaemonTask):
                task: Task[None] = create_task(daemon_task.start(self.__task_signal))
                self.__running_tasks.append(task)
        yield
        self.__task_signal.set()
        self.__thread_signal.set()
        for running_task in self.__running_tasks:
            if isinstance(running_task, Task):
                await running_task
            if isinstance(running_task, Thread):
                running_task.join()
        self.__running_tasks.clear()

    def __initialize_controllers(self) -> None:
        controllers: list[type[IController]] = [
            x for x in self.__context._class_container.values() if issubclass(x, IController)
        ]
        for controller in controllers:
            router: APIRouter = APIRouter(prefix=controller.__prefix__, tags=controller.__tags__)
            for endpoint in controller.__endpoints__:
                router.add_api_route(
                    endpoint=partial(endpoint.method, self=self.__context.retrieve(controller)),
                    **dataclasses.asdict(endpoint.args),
                )
            for websocket in controller.__websockets__:
                router.add_api_websocket_route(
                    endpoint=partial(websocket.method, self=self.__context.retrieve(controller)),
                    **dataclasses.asdict(websocket.args),
                )
            try:
                super().include_router(router=router)
                self.__controllers.append(controller)
            except Exception as e:
                raise e from e

    def inject_middleware(self, middleware_class: type, **options) -> Self:
        super().add_middleware(middleware_class, **options)
        return self

    def inject_background_task(self, async_task: type[IDaemonTask | IAsyncDaemonTask]) -> Self:
        self.__daemon_tasks.append(async_task())
        return self
