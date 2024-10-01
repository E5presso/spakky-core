from abc import ABC
from typing import Callable
from dataclasses import dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import Func


@dataclass
class PointCut(FunctionAnnotation, ABC):
    pointcut: Callable[[Func], bool]

    def matches(self, method: Func) -> bool:
        return self.pointcut(method)


@dataclass
class Before(PointCut): ...


@dataclass
class AfterReturning(PointCut): ...


@dataclass
class AfterRaising(PointCut): ...


@dataclass
class After(PointCut): ...


@dataclass
class Around(PointCut): ...
