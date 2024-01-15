from typing import Any, TypeVar, Callable, Awaitable, ParamSpec
from functools import wraps
from dataclasses import dataclass

from spakky.core.annotation import Annotation

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class Aspect(Annotation):
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

    def __call__(self, obj: Callable[P, R]) -> Callable[P, R]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, R]): Origin function to wrapped by Aspect

        Returns:
            Callable[P, R]: Wrapped function
        """
        obj = super().__call__(obj)

        @wraps(obj)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self.before(*args, **kwargs)
            try:
                result: R = self.around(obj, *args, **kwargs)
                self.after_returning(result)
                return result
            except Exception as e:
                self.after_raising(e)
                raise e from e
            finally:
                self.after()

        return wrapper

    def before(self, *_args: Any, **_kwargs: Any) -> None:
        return

    def after_returning(self, _result: Any) -> None:
        return

    def after_raising(self, _error: Exception) -> None:
        return

    def after(self) -> None:
        return

    def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)


@dataclass
class AsyncAspect(Annotation):
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

    def __call__(self, obj: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, Awaitable[R]]): Origin async function to wrapped by Aspect

        Returns:
            Callable[P, Awaitable[R]]: Wrapped async function
        """
        obj = super().__call__(obj)

        @wraps(obj)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            await self.before(*args, **kwargs)
            try:
                result: R = await self.around(obj, *args, **kwargs)
                await self.after_returning(result)
                return result
            except Exception as e:
                await self.after_raising(e)
                raise e from e
            finally:
                await self.after()

        return wrapper

    async def before(self, *_args: Any, **_kwargs: Any) -> None:
        return

    async def after_returning(self, _result: Any) -> None:
        return

    async def after_raising(self, _error: Exception) -> None:
        return

    async def after(self) -> None:
        return

    async def around(
        self, func: Callable[P, Awaitable[R]], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        return await func(*args, **kwargs)
