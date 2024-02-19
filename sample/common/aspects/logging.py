from uuid import UUID, uuid4
from typing import Callable, Awaitable
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advice import Aspect, AsyncAdvice, AsyncPointcut, P, R
from spakky.core.generics import FuncT
from spakky.dependency.autowired import autowired


@Aspect()
class AsyncLoggingAdvice(AsyncAdvice):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    async def around(
        self, func: Callable[P, Awaitable[R]], *_args: P.args, **_kwargs: P.kwargs
    ) -> R:
        args: str = ", ".join(f"{arg!r}" for arg in _args) if any(_args) else ""
        kwargs: str = (
            ", ".join(f"{key}={value!r}" for key, value in _kwargs.items())
            if any(_kwargs)
            else ""
        )
        trace_id: UUID = uuid4()
        self.__logger.info(f"[Log][{trace_id}] {func.__qualname__}({args}{kwargs})")
        try:
            result: R = await super().around(func, *_args, **_kwargs)
        except Exception as e:
            self.__logger.error(
                f"[Log][{trace_id}] {func.__qualname__} raised {type(e).__name__}"
            )
            raise
        self.__logger.info(f"[Log][{trace_id}] {func.__qualname__} -> {result!r}")
        return result


@dataclass
class AsyncLogging(AsyncPointcut):
    advice = AsyncLoggingAdvice


def async_logging(obj: FuncT) -> FuncT:
    return AsyncLogging()(obj)
