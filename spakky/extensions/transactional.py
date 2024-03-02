from typing import Any
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advice import Around
from spakky.aop.advisor import IAsyncAdvisor
from spakky.aop.aspect import AsyncAspect
from spakky.bean.autowired import autowired
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc
from spakky.domain.infrastructures.persistency.transaction import (
    AbstractAsyncTranasction,
)


@dataclass
class AsyncTransactional(FunctionAnnotation):
    ...


@AsyncAspect()
class AsyncTransactionalAdvisor(IAsyncAdvisor):
    __transacntion: AbstractAsyncTranasction
    __logger: Logger

    @autowired
    def __init__(self, transaction: AbstractAsyncTranasction, logger: Logger) -> None:
        super().__init__()
        self.__transacntion = transaction
        self.__logger = logger

    @Around(AsyncTransactional.contains)
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
