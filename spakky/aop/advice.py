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
    """`Aspect` class is made to support Aspect Oriented Programming.\n
    You can override joinpoint such as\n
    [`before`, `after_returning`, `after_raising`, `after`, `around`]\n
    This is Proxy Wrapper for Callable object.\n
    Here is a example.\n
    ```python
    class AroundAspect(Aspect):
        def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
            assert not args
            assert kwargs == {"name": "John", "age": 30}
            result: R = func(*args, **kwargs)
            assert result == "John30"
            return result

    @AroundAspect()
    def func(name: str, age: int) -> str:
        return name + str(age)

    assert func(name="John", age=30) == "John30"
    ```
    """

    @final
    def __call__(self, pointcut: "Pointcut", function: Callable[P, R]) -> Callable[P, R]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, R]): Origin function to wrapped by Aspect

        Returns:
            Callable[P, R]: Wrapped function
        """

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
        """This pointcut is called before target function\n
        You can reference positional argument (`_args`) and keyword argument (`_kwargs`)\n
        But you cannot modify them.
        """
        return

    def after_returning(self, _pointcut: "Pointcut", _result: Any) -> None:
        """This pointcut is called after target function returned\n
        You can reference result of target function (`_result`)\n
        But you cannot modify them.

        Args:
            _result (Any): Result of target function
        """
        return

    def after_raising(self, _pointcut: "Pointcut", _error: Exception) -> None:
        """This pointcut is called after target function raised Error\n
        You can reference error from target function (`_error`)\n
        But you cannot re-raise from them.

        Args:
            _error (Exception): Raised error from target function
        """
        return

    def after(self, _pointcut: "Pointcut") -> None:
        """This pointcut is always called regardless of error occurrence\n
        or result return after the execution of the target function."""
        return

    def around(
        self,
        _pointcut: "Pointcut",
        func: Callable[P, R],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        """This pointcut is called before target function is called.\n
        You can reference input arguments and also the target funcion\n
        You need to call target function manualy to get the result from target\n
        You can modify input or even result of target function\n
        But you should be careful when you modify them.

        Args:
            func (Callable[P, R]): Target function

        Returns:
            R: Result of target function (can be modified by you)
        """
        return func(*_args, **_kwargs)


class AsyncAdvice(ABC):
    """`AsyncAspect` class is made to support Aspect Oriented Programming.\n
    You can override joinpoint such as\n
    [`before`, `after_returning`, `after_raising`, `after`, `around`]\n
    This is Proxy Wrapper for Callable object.\n
    Here is a example.\n
    ```python
    class AroundAspect(AsyncAspect):
        async def around(
            self, func: Callable[P, Awaitable[R]], *args: P.args, **kwargs: P.kwargs
        ) -> R:
            assert not args
            assert kwargs == {"name": "John", "age": 30}
            result: R = await func(*args, **kwargs)
            assert result == "John30"
            return result


    @AroundAspect()
    async def func(name: str, age: int) -> str:
        return name + str(age)


    assert await func(name="John", age=30) == "John30"
    ```
    """

    @final
    def __call__(
        self, pointcut: "AsyncPointcut", function: Callable[P, Awaitable[R]]
    ) -> Callable[P, Awaitable[R]]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, Awaitable[R]]): Origin async function to wrapped by Aspect

        Returns:
            Callable[P, Awaitable[R]]: Wrapped async function
        """

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
        """This pointcut is called before target function\n
        You can reference positional argument (`_args`) and keyword argument (`_kwargs`)\n
        But you cannot modify them.
        """
        return

    async def after_returning(self, _pointcut: "AsyncPointcut", _result: Any) -> None:
        """This pointcut is called after target function returned\n
        You can reference result of target function (`_result`)\n
        But you cannot modify them.

        Args:
            _result (Any): Result of target function
        """
        return

    async def after_raising(self, _pointcut: "AsyncPointcut", _error: Exception) -> None:
        """This pointcut is called after target function raised Error\n
        You can reference error from target function (`_error`)\n
        But you cannot re-raise from them.

        Args:
            _error (Exception): Raised error from target function
        """
        return

    async def after(self, _pointcut: "AsyncPointcut") -> None:
        """This pointcut is always called regardless of error occurrence\n
        or result return after the execution of the target function."""
        return

    async def around(
        self,
        _pointcut: "AsyncPointcut",
        func: Callable[P, Awaitable[R]],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        """This pointcut is called before target function is called.\n
        You can reference input arguments and also the target funcion\n
        You need to call target function manualy to get the result from target\n
        You can modify input or even result of target function\n
        But you should be careful when you modify them.

        Args:
            func (Callable[P, Awaitable[R]]): Target function

        Returns:
            R: Result of target function (can be modified by you)
        """
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
