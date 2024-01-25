from abc import ABC
from typing import Hashable
from functools import reduce
from dataclasses import astuple

from spakky.architecture.model.decorator import immutable
from spakky.core.equatable import IEquatable


@immutable
class ValueObject(IEquatable, ABC):
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, type(self)):
            return False
        return astuple(self) == astuple(__value)

    def __ne__(self, __value: object) -> bool:
        return not self == __value

    def __hash__(self) -> int:
        return reduce(
            lambda x, y: x ^ y,
            (hash(x) for x in astuple(self) if isinstance(x, Hashable)),
            0,
        )
