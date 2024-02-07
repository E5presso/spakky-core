from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class IManagedRegistry(Protocol):
    @abstractmethod
    def register_managed_component(self, component: type) -> None:
        """Manually register component to context

        Args:
            component (type): Component class to register

        Raises:
            CannotRegisterNonComponentError: Cannot register non-component class
        """
        ...
