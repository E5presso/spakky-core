from typing import Any, TypeVar, Protocol, runtime_checkable
from inspect import getmembers
from dataclasses import dataclass

from spakky.aop.error import AspectInheritanceError
from spakky.aop.pointcut import (
    After,
    AfterRaising,
    AfterReturning,
    Around,
    Before,
    PointCut,
)
from spakky.core.types import AsyncFunc, Func
from spakky.pod.pod import Pod, is_class_pod


@runtime_checkable
class IAspect(Protocol):
    def before(self, *args: Any, **kwargs: Any) -> None:
        return

    def after_raising(self, error: Exception) -> None:
        return

    def after_returning(self, result: Any) -> None:
        return

    def after(self) -> None:
        return

    def around(
        self,
        joinpoint: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return joinpoint(*args, **kwargs)


@runtime_checkable
class IAsyncAspect(Protocol):
    async def before_async(self, *args: Any, **kwargs: Any) -> None:
        return

    async def after_raising_async(self, error: Exception) -> None:
        return

    async def after_returning_async(self, result: Any) -> None:
        return

    async def after_async(self) -> None:
        return

    async def around_async(
        self,
        joinpoint: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return await joinpoint(*args, **kwargs)


AspectT = TypeVar("AspectT", bound=type[IAspect])
AsyncAspectT = TypeVar("AsyncAspectT", bound=type[IAsyncAspect])


@dataclass(eq=False)
class Aspect(Pod):
    def matches(self, pod: object) -> bool:
        if not is_class_pod(self.target):
            raise AspectInheritanceError
        if not issubclass(self.target, IAspect):
            raise AspectInheritanceError
        pointcuts: dict[type[PointCut], Func] = {
            Before: self.target.before,
            AfterReturning: self.target.after_returning,
            AfterRaising: self.target.after_raising,
            After: self.target.after,
            Around: self.target.around,
        }
        for _, method in getmembers(pod, callable):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False


@dataclass(eq=False)
class AsyncAspect(Pod):
    def matches(self, pod: object) -> bool:
        if not is_class_pod(self.target):
            raise AspectInheritanceError
        if not issubclass(self.target, IAsyncAspect):
            raise AspectInheritanceError
        pointcuts: dict[type[PointCut], AsyncFunc] = {
            Before: self.target.before_async,
            AfterReturning: self.target.after_returning_async,
            AfterRaising: self.target.after_raising_async,
            After: self.target.after_async,
            Around: self.target.around_async,
        }
        for _, method in getmembers(pod, callable):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False
