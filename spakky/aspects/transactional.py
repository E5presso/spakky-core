from dataclasses import dataclass
from inspect import iscoroutinefunction
from typing import Any

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.interfaces.aspect import IAspect, IAsyncAspect
from spakky.aop.pointcut import Around
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, Func
from spakky.domain.ports.persistency.transaction import (
    AbstractAsyncTransaction,
    AbstractTransaction,
)
from spakky.pod.annotations.order import Order


@dataclass
class Transactional(FunctionAnnotation): ...


@Order(0)
@AsyncAspect()
class AsyncTransactionalAspect(IAsyncAspect):
    __transacntion: AbstractAsyncTransaction

    def __init__(self, transaction: AbstractAsyncTransaction) -> None:
        super().__init__()
        self.__transacntion = transaction

    @Around(lambda x: Transactional.exists(x) and iscoroutinefunction(x))
    async def around_async(
        self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any
    ) -> Any:
        try:
            async with self.__transacntion:
                result = await joinpoint(*args, **kwargs)
        except:
            raise
        return result


@Order(0)
@Aspect()
class TransactionalAspect(IAspect):
    __transaction: AbstractTransaction

    def __init__(self, transaction: AbstractTransaction) -> None:
        super().__init__()
        self.__transaction = transaction

    @Around(lambda x: Transactional.exists(x) and not iscoroutinefunction(x))
    def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
        try:
            with self.__transaction:
                result = joinpoint(*args, **kwargs)
        except:
            raise
        return result
