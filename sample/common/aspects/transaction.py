from typing import Callable, Awaitable
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advice import Aspect, AsyncAdvice, AsyncPointcut, P, R
from spakky.core.generics import FuncT
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.unit_of_work import AbstractAsyncUnitOfWork


@Aspect()
class AsyncTransactionalAdvice(AsyncAdvice):
    __transacntion: AbstractAsyncUnitOfWork
    __logger: Logger

    @autowired
    def __init__(self, transaction: AbstractAsyncUnitOfWork, logger: Logger) -> None:
        super().__init__()
        self.__transacntion = transaction
        self.__logger = logger

    async def around(
        self, func: Callable[P, Awaitable[R]], *_args: P.args, **_kwargs: P.kwargs
    ) -> R:
        self.__logger.info("[Transaction] BEGIN TRANSACTION")
        try:
            async with self.__transacntion:
                result: R = await super().around(func, *_args, **_kwargs)
        except:
            self.__logger.info("[Transaction] ROLLBACK")
            raise
        self.__logger.info("[Transaction] COMMIT")
        return result


@dataclass
class AsyncTransactional(AsyncPointcut):
    advice = AsyncTransactionalAdvice


def async_transactional(obj: FuncT) -> FuncT:
    return AsyncTransactional()(obj)
