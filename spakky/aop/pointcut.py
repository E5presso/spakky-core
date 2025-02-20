from abc import ABC
from dataclasses import dataclass
from typing import Callable

from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import Func


@dataclass
class AbstractPointCut(FunctionAnnotation, ABC):
    pointcut: Callable[[Func], bool]

    def matches(self, method: Func) -> bool:
        return self.pointcut(method)


@dataclass
class Before(AbstractPointCut): ...


@dataclass
class AfterReturning(AbstractPointCut): ...


@dataclass
class AfterRaising(AbstractPointCut): ...


@dataclass
class After(AbstractPointCut): ...


@dataclass
class Around(AbstractPointCut): ...
