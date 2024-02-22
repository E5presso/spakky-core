from abc import ABC
from typing import Any, TypeVar, Callable, ClassVar, Awaitable, ParamSpec, final
from functools import wraps
from dataclasses import dataclass

from spakky.bean.bean import Bean
from spakky.core.annotation import FunctionAnnotation
from spakky.core.generics import AsyncFuncT

P = ParamSpec("P")
R = TypeVar("R")


class Advice(ABC):
    @final
    def __call__(self, pointcut: "Pointcut", function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self.before(pointcut, *args, **kwargs)
            try:
                result: R = self.around(pointcut, function, *args, **kwargs)
                self.after_returning(pointcut, result)
                return result
            except Exception as e:
                self.after_raising(pointcut, e)
                raise
            finally:
                self.after(pointcut)

        return wrapper

    def before(self, _pointcut: "Pointcut", *_args: Any, **_kwargs: Any) -> None:
        return

    def after_returning(self, _pointcut: "Pointcut", _result: Any) -> None:
        return

    def after_raising(self, _pointcut: "Pointcut", _error: Exception) -> None:
        return

    def after(self, _pointcut: "Pointcut") -> None:
        return

    def around(
        self,
        _pointcut: "Pointcut",
        func: Callable[P, R],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        return func(*_args, **_kwargs)


class AsyncAdvice(ABC):
    @final
    def __call__(
        self, pointcut: "AsyncPointcut", function: Callable[P, Awaitable[R]]
    ) -> Callable[P, Awaitable[R]]:
        @wraps(function)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            await self.before(pointcut, *args, **kwargs)
            try:
                result: R = await self.around(pointcut, function, *args, **kwargs)
                await self.after_returning(pointcut, result)
                return result
            except Exception as e:
                await self.after_raising(pointcut, e)
                raise
            finally:
                await self.after(pointcut)

        return wrapper

    async def before(
        self, _pointcut: "AsyncPointcut", *_args: Any, **_kwargs: Any
    ) -> None:
        return

    async def after_returning(self, _pointcut: "AsyncPointcut", _result: Any) -> None:
        return

    async def after_raising(self, _pointcut: "AsyncPointcut", _error: Exception) -> None:
        return

    async def after(self, _pointcut: "AsyncPointcut") -> None:
        return

    async def around(
        self,
        _pointcut: "AsyncPointcut",
        func: Callable[P, Awaitable[R]],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        return await func(*_args, **_kwargs)


AdviceT = TypeVar("AdviceT", bound=type[Advice | AsyncAdvice])


@dataclass
class Aspect(Bean):
    def __call__(self, obj: AdviceT) -> AdviceT:
        return super().__call__(obj)


@dataclass
class Pointcut(FunctionAnnotation):
    advice: ClassVar[type[Advice]]


@dataclass
class AsyncPointcut(FunctionAnnotation):
    advice: ClassVar[type[AsyncAdvice]]

    def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
        return super().__call__(obj)
