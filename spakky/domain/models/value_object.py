from abc import ABC
from copy import deepcopy
from typing import Self, Hashable
from functools import reduce
from dataclasses import astuple

from spakky.core.interfaces.cloneable import ICloneable
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mutability import immutable


@immutable
class ValueObject(IEquatable, ICloneable, ABC):
    def clone(self) -> Self:
        return deepcopy(self)

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
