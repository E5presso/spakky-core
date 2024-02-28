from types import MethodType
from typing import Callable
from dataclasses import dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFuncT


@dataclass
class _Pointcut(FunctionAnnotation):
    pointcut: Callable[[MethodType], bool]

    def is_matched(self, method: MethodType) -> bool:
        return self.pointcut(method)


@dataclass
class Before(_Pointcut):
    ...


@dataclass
class AfterReturning(_Pointcut):
    ...


@dataclass
class AfterRaising(_Pointcut):
    ...


@dataclass
class After(_Pointcut):
    ...


@dataclass
class Around(_Pointcut):
    ...


@dataclass
class AsyncBefore(_Pointcut):
    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)


@dataclass
class AsyncAfterReturning(_Pointcut):
    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)


@dataclass
class AsyncAfterRaising(_Pointcut):
    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)


@dataclass
class AsyncAfter(_Pointcut):
    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)


@dataclass
class AsyncAround(_Pointcut):
    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)
