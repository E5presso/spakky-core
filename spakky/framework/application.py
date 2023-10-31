from dataclasses import dataclass, asdict
from typing import Any, AsyncGenerator, Self
from contextlib import asynccontextmanager
from functools import partial
from asyncio import Event, Task, create_task
from threading import Thread, Event as ThreadEvent

from fastapi import APIRouter, FastAPI
from spakky.framework.context.application_context import ApplicationContext
from spakky.framework.context.component_scan import ComponentScan
from spakky.framework.context.stereotype.async_task import AsyncTask, IAsyncTask
from spakky.framework.context.stereotype.controller import Controller
from spakky.framework.context.stereotype.task import ISyncTask, SyncTask


@dataclass
class SpakkyBootApplication(ComponentScan):
    ...


class SpakkyApplication(FastAPI):
    __context: ApplicationContext
    __tasks: list[ISyncTask | IAsyncTask]
    __running_tasks: list[Task[None] | Thread]
    __task_signal: Event
    __thread_signal: ThreadEvent

    @property
    def context(self) -> ApplicationContext:
        return self.__context

    def __init__(self, app: Any, *args, **kwargs) -> None:
        annotation: SpakkyBootApplication | None = SpakkyBootApplication.get_annotation(app)
        if annotation is None:
            raise RuntimeError("Cannot Initialize App from parameter 'app'.")
        super().__init__(*args, **kwargs)
        self.__context = annotation.context
        self.__tasks = []
        self.__running_tasks = []
        self.__task_signal = Event()
        self.__thread_signal = ThreadEvent()
        self.__initialize_controllers()
        self.__initialize_tasks()
        self.router.lifespan_context = self.__app_lifecycle_hook

    @asynccontextmanager
    async def __app_lifecycle_hook(self, _: Self) -> AsyncGenerator[None, None]:
        for _task in self.__tasks:
            if isinstance(_task, ISyncTask):
                thread: Thread = Thread(target=_task.start, args=(self.__thread_signal,))
                thread.start()
                self.__running_tasks.append(thread)
                continue
            if isinstance(_task, IAsyncTask):
                task: Task[None] = create_task(_task.start(self.__task_signal))
                self.__running_tasks.append(task)
                continue
            raise RuntimeError(
                "Class decorated by @SyncTask or @AsyncTask must be inherited from ISyncTask or IAsyncTask interface"
            )
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
        controllers: set[type] = {x for x in self.__context.class_container.values() if Controller.has_annotation(x)}
        for controller in controllers:
            annotation: Controller | None = Controller.get_annotation(controller)
            if annotation is None:
                raise RuntimeError(f"Cannot find 'Controller' annotations in '{controller}'")
            router: APIRouter = APIRouter(prefix=annotation.prefix, tags=annotation.tags)
            for endpoint in annotation.endpoints:
                router.add_api_route(
                    endpoint=partial(endpoint.method, self=self.__context.retrieve(controller)),
                    **asdict(endpoint.args),
                )
            for websocket in annotation.websockets:
                router.add_api_websocket_route(
                    endpoint=partial(websocket.method, self=self.__context.retrieve(controller)),
                    **asdict(websocket.args),
                )
            try:
                super().include_router(router=router)
            except Exception as e:
                raise e from e

    def __initialize_tasks(self) -> None:
        [
            self.__tasks.append(self.__context.retrieve(x))
            for x in self.__context.class_container.values()
            if SyncTask.has_annotation(x) or AsyncTask.has_annotation(x)
        ]

    def inject_middleware(self, middleware_class: type, **options) -> Self:
        super().add_middleware(middleware_class, **options)
        return self
