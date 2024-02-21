from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.bean.bean import BeanFactoryType
from spakky.bean.error import SpakkyBeanError


class CannotRegisterNonBeanError(SpakkyBeanError):
    """Cannot register non bean class.\n
    The bean class must be decorated by `@Bean()`
    """

    message = "Cannot register non-bean class."


class CannotRegisterNonBeanFactoryError(SpakkyBeanError):
    """Cannot register non-bean class.\n
    The bean factory must be decorated by `@BeanFactory()`
    """

    message = "Cannot register non bean-factory function."


@runtime_checkable
class IBeanRegistry(Protocol):
    @abstractmethod
    def register_bean(self, bean: type) -> None:
        """Manually register bean to context

        Args:
            bean (type): Bean class to register

        Raises:
            CannotRegisterNonBeanError: Cannot register non bean class
        """
        ...

    @abstractmethod
    def register_bean_factory(self, factory: BeanFactoryType) -> None:
        ...
