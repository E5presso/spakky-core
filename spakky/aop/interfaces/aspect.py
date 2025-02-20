from typing import Any, Protocol, TypeVar, runtime_checkable

from spakky.core.types import AsyncFunc, Func


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
