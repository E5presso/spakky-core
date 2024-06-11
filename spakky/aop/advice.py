from typing import Callable
from dataclasses import dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import Func


@dataclass
class _Advice(FunctionAnnotation):
    pointcut: Callable[[Func], bool]

    def matches(self, method: Func) -> bool:
        return self.pointcut(method)


@dataclass
class Before(_Advice): ...


@dataclass
class AfterReturning(_Advice): ...


@dataclass
class AfterRaising(_Advice): ...


@dataclass
class After(_Advice): ...


@dataclass
class Around(_Advice): ...
