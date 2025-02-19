from abc import abstractmethod
from typing import Protocol, runtime_checkable
from logging import Logger

from spakky.pod.interfaces.aware.aware import IAware


@runtime_checkable
class ILoggerAware(IAware, Protocol):
    @abstractmethod
    def set_logger(self, logger: Logger) -> None: ...
