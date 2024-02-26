import re
from typing import Callable, ClassVar, Awaitable
from logging import Logger
from dataclasses import field, dataclass

from spakky.aop.advice import AbstractAsyncAdvice, Aspect, AsyncPointcut, P, R
from spakky.bean.autowired import autowired


@Aspect()
class AsyncLoggingAdvice(AbstractAsyncAdvice):
    MASKING_TEXT: ClassVar[str] = r"\2'******'"
    MASKING_REGEX: ClassVar[
        str
    ] = r"((['\"]?(?={keys})[^'\"]*['\"]?[:=]\s*)['\"][^'\"]*['\"])"
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    async def around(
        self,
        _pointcut: "AsyncLogging",
        func: Callable[P, Awaitable[R]],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        masking_keys: str = "|".join(_pointcut.masking_keys)
        masking_regex: str = self.MASKING_REGEX.format(keys=masking_keys)
        mask: re.Pattern[str] | None = re.compile(masking_regex)
        args: str = ", ".join(f"{arg!r}" for arg in _args) if any(_args) else ""
        kwargs: str = (
            ", ".join(f"{key}={value!r}" for key, value in _kwargs.items())
            if any(_kwargs)
            else ""
        )

        before: str = f"[Log] {func.__qualname__}({args}{kwargs})"
        self.__logger.info(
            mask.sub(self.MASKING_TEXT, before) if _pointcut.enable_masking else before
        )

        try:
            result: R = await super().around(_pointcut, func, *_args, **_kwargs)
        except Exception as e:
            error: str = (
                f"[Log] {func.__qualname__}({args}{kwargs}) raised {type(e).__name__}"
            )
            self.__logger.error(
                mask.sub(self.MASKING_TEXT, error) if _pointcut.enable_masking else error
            )
            raise
        after: str = f"[Log] {func.__qualname__}({args}{kwargs}) -> {result!r}"
        self.__logger.info(
            mask.sub(self.MASKING_TEXT, after) if _pointcut.enable_masking else after
        )
        return result


@dataclass
class AsyncLogging(AsyncPointcut):
    advice = AsyncLoggingAdvice

    enable_masking: bool = True
    masking_keys: list[str] = field(default_factory=lambda: ["secret", "key", "password"])
