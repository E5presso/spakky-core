from abc import ABC
from typing import Callable
from dataclasses import dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import Func


@dataclass
class _PointCut(FunctionAnnotation, ABC):
    pointcut: Callable[[Func], bool]

    def matches(self, method: Func) -> bool:
        return self.pointcut(method)


@dataclass
class Before(_PointCut): ...


@dataclass
class AfterReturning(_PointCut): ...


@dataclass
class AfterRaising(_PointCut): ...


@dataclass
class After(_PointCut): ...


@dataclass
class Around(_PointCut): ...
