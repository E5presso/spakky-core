from typing import Callable, Awaitable
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advisor import AsyncAdvisor, AsyncAspect, P, R
from spakky.aop.pointcut import AsyncPointcut
from spakky.core.generics import FuncT
from spakky.dependency.autowired import autowired


@AsyncAspect()
class AsyncLoggingAdvisor(AsyncAdvisor):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    async def around(
        self, func: Callable[P, Awaitable[R]], *_args: P.args, **_kwargs: P.kwargs
    ) -> R:
        try:
            result: R = await super().around(func, *_args, **_kwargs)
        except Exception as e:
            self.__logger.error(f"raised {e!r}", exc_info=e)
            raise
        args = f"{_args!r}, " if any(_args) else ""
        kwargs = f"{_kwargs!r}" if any(_kwargs) else ""
        self.__logger.info(f"{func.__qualname__}({args}{kwargs}) -> {result!r}")
        return result


@dataclass
class AsyncLogging(AsyncPointcut):
    advisor = AsyncLoggingAdvisor


def async_logging(obj: FuncT) -> FuncT:
    return AsyncLogging()(obj)
