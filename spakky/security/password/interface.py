from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.core.interfaces.equatable import IEquatable
from spakky.core.interfaces.representable import IRepresentable


@runtime_checkable
class IPasswordEncoder(IEquatable, IRepresentable, Protocol):
    @abstractmethod
    def encode(self) -> str: ...

    @abstractmethod
    def challenge(self, password: str) -> bool: ...
