from abc import ABC
from typing import Any, TypeVar, Callable, Awaitable, ParamSpec
from functools import wraps
from dataclasses import dataclass

from spakky.dependency.component import Component

P = ParamSpec("P")
R = TypeVar("R")


class Advisor(ABC):
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

    def __call__(self, function: Callable[P, R]) -> Callable[P, R]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, R]): Origin function to wrapped by Aspect

        Returns:
            Callable[P, R]: Wrapped function
        """

        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self.before(*args, **kwargs)
            try:
                result: R = self.around(function, *args, **kwargs)
                self.after_returning(result)
                return result
            except Exception as e:
                self.after_raising(e)
                raise
            finally:
                self.after()

        return wrapper

    def before(self, *_args: Any, **_kwargs: Any) -> None:
        """This pointcut is called before target function\n
        You can reference positional argument (`_args`) and keyword argument (`_kwargs`)\n
        But you cannot modify them.
        """
        return

    def after_returning(self, _result: Any) -> None:
        """This pointcut is called after target function returned\n
        You can reference result of target function (`_result`)\n
        But you cannot modify them.

        Args:
            _result (Any): Result of target function
        """
        return

    def after_raising(self, _error: Exception) -> None:
        """This pointcut is called after target function raised Error\n
        You can reference error from target function (`_error`)\n
        But you cannot re-raise from them.

        Args:
            _error (Exception): Raised error from target function
        """
        return

    def after(self) -> None:
        """This pointcut is always called regardless of error occurrence\n
        or result return after the execution of the target function."""
        return

    def around(self, func: Callable[P, R], *_args: P.args, **_kwargs: P.kwargs) -> R:
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


class AsyncAdvisor(ABC):
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

    def __call__(self, function: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, Awaitable[R]]): Origin async function to wrapped by Aspect

        Returns:
            Callable[P, Awaitable[R]]: Wrapped async function
        """

        @wraps(function)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            await self.before(*args, **kwargs)
            try:
                result: R = await self.around(function, *args, **kwargs)
                await self.after_returning(result)
                return result
            except Exception as e:
                await self.after_raising(e)
                raise e
            finally:
                await self.after()

        return wrapper

    async def before(self, *_args: Any, **_kwargs: Any) -> None:
        """This pointcut is called before target function\n
        You can reference positional argument (`_args`) and keyword argument (`_kwargs`)\n
        But you cannot modify them.
        """
        return

    async def after_returning(self, _result: Any) -> None:
        """This pointcut is called after target function returned\n
        You can reference result of target function (`_result`)\n
        But you cannot modify them.

        Args:
            _result (Any): Result of target function
        """
        return

    async def after_raising(self, _error: Exception) -> None:
        """This pointcut is called after target function raised Error\n
        You can reference error from target function (`_error`)\n
        But you cannot re-raise from them.

        Args:
            _error (Exception): Raised error from target function
        """
        return

    async def after(self) -> None:
        """This pointcut is always called regardless of error occurrence\n
        or result return after the execution of the target function."""
        return

    async def around(
        self, func: Callable[P, Awaitable[R]], *_args: P.args, **_kwargs: P.kwargs
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


AdvisorT = TypeVar("AdvisorT", bound=type[Advisor])
AsyncAdvisorT = TypeVar("AsyncAdvisorT", bound=type[AsyncAdvisor])


@dataclass
class Aspect(Component):
    def __call__(self, obj: AdvisorT) -> AdvisorT:
        return super().__call__(obj)


@dataclass
class AsyncAspect(Component):
    def __call__(self, obj: AsyncAdvisorT) -> AsyncAdvisorT:
        return super().__call__(obj)
