from abc import abstractmethod
from asyncio import locks
from threading import Event
from typing import Protocol, runtime_checkable

from spakky.application.error import AbstractSpakkyApplicationError
from spakky.pod.interfaces.container import IContainer
from spakky.service.interfaces.service import IAsyncService, IService


class ApplicationContextAlreadyStartedError(AbstractSpakkyApplicationError):
    message = "Application context already started"


class ApplicationContextAlreadyStoppedError(AbstractSpakkyApplicationError):
    message = "Application context already stopped"


class EventLoopThreadNotStartedInApplicationContextError(
    AbstractSpakkyApplicationError
):
    message = "Event loop thread not started in application context"


class EventLoopThreadAlreadyStartedInApplicationContextError(
    AbstractSpakkyApplicationError
):
    message = "Event loop thread already started in application context"


@runtime_checkable
class IApplicationContext(IContainer, Protocol):
    thread_stop_event: Event
    task_stop_event: locks.Event

    @property
    @abstractmethod
    def is_started(self) -> bool: ...

    @abstractmethod
    def add_service(self, service: IService | IAsyncService) -> None: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
