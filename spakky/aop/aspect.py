from typing import Any, TypeVar, Protocol, runtime_checkable
from inspect import getmembers
from dataclasses import field, dataclass

from spakky.aop.pointcut import After, AfterRaising, AfterReturning, Around, Before
from spakky.core.types import AsyncFunc, Func
from spakky.pod.pod import Pod


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


@dataclass
class Aspect(Pod):
    aspect: type[IAspect] = field(init=False)

    def __call__(self, obj: AspectT) -> AspectT:
        self.aspect = obj
        return super().__call__(obj)

    def matches(self, pod: object) -> bool:
        for _, method in getmembers(pod, callable):
            for annotation, target_method in {
                Before: self.aspect.before,
                AfterReturning: self.aspect.after_returning,
                AfterRaising: self.aspect.after_raising,
                After: self.aspect.after,
                Around: self.aspect.around,
            }.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False


@dataclass
class AsyncAspect(Pod):
    aspect: type[IAsyncAspect] = field(init=False)

    def __call__(self, obj: AsyncAspectT) -> AsyncAspectT:
        self.aspect = obj
        return super().__call__(obj)

    def matches(self, pod: object) -> bool:
        for _, method in getmembers(pod, callable):
            for annotation, target_method in {
                Before: self.aspect.before_async,
                AfterReturning: self.aspect.after_returning_async,
                AfterRaising: self.aspect.after_raising_async,
                After: self.aspect.after_async,
                Around: self.aspect.around_async,
            }.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False
