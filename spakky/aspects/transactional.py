from typing import Any
from logging import Logger
from dataclasses import dataclass

from spakky.aop.aspect import AsyncAspect
from spakky.aop.pointcut import AsyncAround
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc
from spakky.domain.interfaces.transaction import AbstractAsyncTranasction


@dataclass
class AsyncTransactional(FunctionAnnotation):
    ...


@AsyncAspect()
class AsyncTransactionalAdvice:
    __transacntion: AbstractAsyncTranasction
    __logger: Logger

    @autowired
    def __init__(self, transaction: AbstractAsyncTranasction, logger: Logger) -> None:
        super().__init__()
        self.__transacntion = transaction
        self.__logger = logger

    @AsyncAround(AsyncTransactional.contains)
    async def around(
        self,
        joinpoint: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        self.__logger.info("[Transaction] BEGIN TRANSACTION")
        try:
            async with self.__transacntion:
                result = await joinpoint(*args, **kwargs)
        except:
            self.__logger.info("[Transaction] ROLLBACK")
            raise
        self.__logger.info("[Transaction] COMMIT")
        return result
