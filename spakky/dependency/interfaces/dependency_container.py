from abc import abstractmethod
from typing import Any, Callable, Protocol, Sequence, overload, runtime_checkable

from spakky.core.generics import ObjectT


@runtime_checkable
class IDependencyContainer(Protocol):
    @overload
    @abstractmethod
    def contains(self, *, required_type: type) -> bool:
        """Check existance of component by given condition

        Args:
            required_type (type | None, optional): Required type to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        ...

    @overload
    @abstractmethod
    def contains(self, *, name: str) -> bool:
        """Check existance of component by given condition

        Args:
            name (str | None, optional): Name to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        ...

    @abstractmethod
    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool:
        """Check existance of component by given condition

        Args:
            required_type (type | None, optional): Required type to check existance.
            Defaults to None.
            name (str | None, optional): Name to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        ...

    @overload
    @abstractmethod
    def get(self, *, required_type: type[ObjectT]) -> ObjectT:
        """Retrieve component by given condition

        Args:
            required_type (type[ObjectT] | None, optional): Required type to
            get component. Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            ObjectT: Retrieved component by given condition
        """
        ...

    @overload
    @abstractmethod
    def get(self, *, name: str) -> Any:
        """Retrieve component by given condition

        Args:
            name (str | None, optional): Name to get component.
            Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            object: Retrieved component by given condition
        """

    @abstractmethod
    def get(
        self, required_type: type[ObjectT] | None = None, name: str | None = None
    ) -> ObjectT | Any:
        """Retrieve component by given condition

        Args:
            required_type (type[ObjectT] | None, optional): Required type to
            get component. Defaults to None.
            name (str | None, optional): Name to get component.
            Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            object: Retrieved component by given condition
        """

    @abstractmethod
    def where(self, clause: Callable[[type], bool]) -> Sequence[object]:
        """Query components from context by given clause

        Args:
            clause (Callable[[type], bool]): Given clause to query components

        Returns:
            Sequence[object]: Queried components by given clause
        """
        ...
