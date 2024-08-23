from typing import Any
from dataclasses import dataclass

from spakky.aop.advice import Around
from spakky.aop.aspect import Aspect, AsyncAspect, IAspect, IAsyncAspect
from spakky.aop.order import Order
from spakky.aspects.logging import Logging
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, Func
from spakky.security.key import Key
from spakky.stereotype.usecase import UseCase


@dataclass
class Dummy(FunctionAnnotation): ...


@dataclass
class AsyncDummy(FunctionAnnotation): ...


@Order(0)
@Aspect()
class DummyAdvisor(IAspect):
    @Around(Dummy.exists)
    def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
        _annotation = Dummy.get(joinpoint)
        return joinpoint(*args, **kwargs)


@Order(0)
@AsyncAspect()
class AsyncDummyAdvisor(IAsyncAspect):
    @Around(AsyncDummy.exists)
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        _annotation = AsyncDummy.get(joinpoint)
        return await joinpoint(*args, **kwargs)


@UseCase()
class DummyUseCase:
    __key: Key

    @property
    def key(self) -> Key:
        return self.__key

    def __init__(self, key: Key) -> None:
        self.__key = key

    @Logging()
    @Dummy()
    def execute(self) -> str:
        return "Hello, World!"


@UseCase()
class AsyncDummyUseCase:
    __key: Key

    @property
    def key(self) -> Key:
        return self.__key

    def __init__(self, key: Key) -> None:
        self.__key = key

    @Logging()
    @AsyncDummy()
    async def execute(self) -> str:
        return "Hello, World!"
