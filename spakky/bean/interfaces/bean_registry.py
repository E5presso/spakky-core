from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.bean.bean import BeanFactoryType
from spakky.bean.error import SpakkyBeanError


class CannotRegisterNonBeanError(SpakkyBeanError):
    message = "Cannot register non-bean class."


class CannotRegisterNonBeanFactoryError(SpakkyBeanError):
    message = "Cannot register non bean-factory function."


@runtime_checkable
class IBeanRegistry(Protocol):
    @abstractmethod
    def register_bean(self, bean: type) -> None:
        ...

    @abstractmethod
    def register_bean_factory(self, factory: BeanFactoryType) -> None:
        ...
