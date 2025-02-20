import sys
from abc import ABC, abstractmethod
from collections.abc import Hashable
from copy import deepcopy
from dataclasses import astuple
from functools import reduce

from spakky.core.interfaces.cloneable import ICloneable
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@immutable
class AbstractValueObject(IEquatable, ICloneable, ABC):
    def clone(self) -> Self:
        return deepcopy(self)

    @abstractmethod
    def validate(self) -> None: ...

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, type(self)):
            return False
        return astuple(self) == astuple(__value)

    def __hash__(self) -> int:
        return reduce(
            lambda x, y: x ^ y,
            (hash(x) for x in astuple(self) if isinstance(x, Hashable)),
            0,
        )

    def __post_init__(self) -> None:
        self.validate()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        for name, type in cls.__annotations__.items():
            if getattr(type, "__hash__", None) is None:
                raise TypeError(f"type of '{name}' is not hashable")
