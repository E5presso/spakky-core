from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.pod.error import AbstractSpakkyPodError
from spakky.pod.interfaces.container import IContainer


class ApplicationContextAlreadyStartedError(AbstractSpakkyPodError):
    message = "Application context already started"


class ApplicationContextAlreadyStoppedError(AbstractSpakkyPodError):
    message = "Application context already stopped"


@runtime_checkable
class IApplicationContext(IContainer, Protocol):
    @property
    @abstractmethod
    def is_started(self) -> bool: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
