from typing import Any
from inspect import iscoroutinefunction
from logging import Logger
from dataclasses import dataclass

from spakky.aop.pointcut import Around
from spakky.aop.aspect import Aspect, AsyncAspect, IAspect, IAsyncAspect
from spakky.pod.order import Order
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, Func
from spakky.domain.ports.persistency.transaction import (
    AbstractAsyncTransaction,
    AbstractTransaction,
)


@dataclass
class Transactional(FunctionAnnotation): ...


@Order(0)
@AsyncAspect()
class AsyncTransactionalAspect(IAsyncAspect):
    __transacntion: AbstractAsyncTransaction
    __logger: Logger

    def __init__(self, transaction: AbstractAsyncTransaction, logger: Logger) -> None:
        super().__init__()
        self.__transacntion = transaction
        self.__logger = logger

    @Around(lambda x: Transactional.exists(x) and iscoroutinefunction(x))
    async def around_async(self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        self.__logger.info(f"[{type(self).__name__}] BEGIN TRANSACTION")
        try:
            async with self.__transacntion:
                result = await joinpoint(*args, **kwargs)
        except:
            self.__logger.info(f"[{type(self).__name__}] ROLLBACK")
            raise
        self.__logger.info(f"[{type(self).__name__}] COMMIT")
        return result


@Order(0)
@Aspect()
class TransactionalAspect(IAspect):
    __transaction: AbstractTransaction
    __logger: Logger

    def __init__(self, transaction: AbstractTransaction, logger: Logger) -> None:
        super().__init__()
        self.__transaction = transaction
        self.__logger = logger

    @Around(lambda x: Transactional.exists(x) and not iscoroutinefunction(x))
    def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
        self.__logger.info(f"[{type(self).__name__}] BEGIN TRANSACTION")
        try:
            with self.__transaction:
                result = joinpoint(*args, **kwargs)
        except:
            self.__logger.info(f"[{type(self).__name__}] ROLLBACK")
            raise
        self.__logger.info(f"[{type(self).__name__}] COMMIT")
        return result
