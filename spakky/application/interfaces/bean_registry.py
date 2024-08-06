from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.bean.bean import BeanFactoryType
from spakky.bean.error import SpakkyBeanError


class CannotRegisterNonBeanObjectError(SpakkyBeanError):
    message = "Cannot register non-bean object."


@runtime_checkable
class IBeanRegistry(Protocol):
    @abstractmethod
    def register_bean(self, bean: type) -> None: ...

    @abstractmethod
    def register_bean_factory(self, factory: BeanFactoryType) -> None: ...
