from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.pod.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.aware.aware import IAware


@runtime_checkable
class IApplicationContextAware(IAware, Protocol):
    @abstractmethod
    def set_application_context(
        self, application_context: IApplicationContext
    ) -> None: ...
