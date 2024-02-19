import re
from time import perf_counter
from typing import Callable, ClassVar, Awaitable
from logging import Logger
from dataclasses import field, dataclass

from sample.common.config import ServerConfiguration
from spakky.aop.advice import Aspect, AsyncAdvice, AsyncPointcut, P, R
from spakky.dependency.autowired import autowired


@Aspect()
class AsyncLoggingAdvice(AsyncAdvice):
    MASK_TEXT: ClassVar[str] = r"\2'******'"
    __logger: Logger
    __debug: bool

    @autowired
    def __init__(self, logger: Logger, config: ServerConfiguration) -> None:
        super().__init__()
        self.__logger = logger
        self.__debug = config.debug

    async def around(
        self,
        _pointcut: "AsyncLogging",
        func: Callable[P, Awaitable[R]],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        mask: re.Pattern[str] | None = re.compile(_pointcut.mask)
        start: float = perf_counter()
        args: str = ", ".join(f"{arg!r}" for arg in _args) if any(_args) else ""
        kwargs: str = (
            ", ".join(f"{key}={value!r}" for key, value in _kwargs.items())
            if any(_kwargs)
            else ""
        )

        before: str = f"[Log] {func.__qualname__}({args}{kwargs})"
        self.__logger.info(
            mask.sub(self.MASK_TEXT, before) if not self.__debug else before
        )
        try:
            result: R = await super().around(_pointcut, func, *_args, **_kwargs)
        except Exception as e:
            elapsed: float = perf_counter() - start
            error: str = f"[Log] {func.__qualname__}({args}{kwargs}) raised {type(e).__name__} ({elapsed:.0f}ms)"
            self.__logger.error(
                mask.sub(self.MASK_TEXT, error) if not self.__debug else error
            )
            raise
        elapsed: float = perf_counter() - start
        after: str = (
            f"[Log] {func.__qualname__}({args}{kwargs}) -> {result!r} ({elapsed:.0f}ms)"
        )
        self.__logger.info(mask.sub(self.MASK_TEXT, after) if not self.__debug else after)
        return result


@dataclass
class AsyncLogging(AsyncPointcut):
    advice = AsyncLoggingAdvice

    mask: str = field(
        default=r"((['\"]?(?=secret|auth|key|password)[^'\"]*['\"]?[:=]\s*)['\"][^'\"]*['\"])"
    )
