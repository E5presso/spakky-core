import re
from time import perf_counter
from typing import Any, ClassVar
from logging import Logger
from dataclasses import field, dataclass

from spakky.aop.advice import Around
from spakky.aop.advisor import IAsyncAdvisor
from spakky.aop.aspect import AsyncAspect
from spakky.aop.order import Order
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc


@dataclass
class AsyncLogging(FunctionAnnotation):
    enable_masking: bool = True
    masking_keys: list[str] = field(default_factory=lambda: ["secret", "key", "password"])


@Order(0)
@AsyncAspect()
class AsyncLoggingAdvisor(IAsyncAdvisor):
    MASKING_TEXT: ClassVar[str] = r"\2'******'"
    MASKING_REGEX: ClassVar[str] = (
        r"((['\"]?(?={keys})[^'\"]*['\"]?[:=]\s*)['\"][^'\"]*['\"])"
    )
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    @Around(AsyncLogging.contains)
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        start: float = perf_counter()
        annotation: AsyncLogging = AsyncLogging.single(joinpoint)
        masking_keys: str = "|".join(annotation.masking_keys)
        masking_regex: str = self.MASKING_REGEX.format(keys=masking_keys)
        mask: re.Pattern[str] | None = re.compile(masking_regex)
        _args: str = ", ".join(f"{arg!r}" for arg in args) if any(args) else ""
        _kwargs: str = (
            ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
            if any(kwargs)
            else ""
        )

        try:
            result = await joinpoint(*args, **kwargs)
        except Exception as e:
            end: float = perf_counter()
            error: str = (
                f"[{type(self).__name__}] {joinpoint.__qualname__}({_args}{_kwargs}) raised {type(e).__name__} ({end - start:.2f}s)"
            )
            self.__logger.error(
                mask.sub(self.MASKING_TEXT, error) if annotation.enable_masking else error
            )
            raise
        end: float = perf_counter()
        after: str = (
            f"[{type(self).__name__}] {joinpoint.__qualname__}({_args}{_kwargs}) -> {result!r} ({end - start:.2f}s)"
        )
        self.__logger.info(
            mask.sub(self.MASKING_TEXT, after) if annotation.enable_masking else after
        )
        return result
