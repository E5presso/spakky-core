from typing import Callable, Awaitable
from logging import Logger
from dataclasses import dataclass

from spakky.aop.advice import AbstractAsyncAdvice, Aspect, AsyncPointcut, P, R
from spakky.bean.autowired import autowired
from spakky.domain.interfaces.transaction import AbstractAsyncTranasction


@Aspect()
class AsyncTransactionalAdvice(AbstractAsyncAdvice):
    __transacntion: AbstractAsyncTranasction
    __logger: Logger

    @autowired
    def __init__(self, transaction: AbstractAsyncTranasction, logger: Logger) -> None:
        super().__init__()
        self.__transacntion = transaction
        self.__logger = logger

    async def around(
        self,
        _pointcut: "AsyncTransactional",
        func: Callable[P, Awaitable[R]],
        *_args: P.args,
        **_kwargs: P.kwargs,
    ) -> R:
        self.__logger.info("[Transaction] BEGIN TRANSACTION")
        try:
            async with self.__transacntion:
                result: R = await super().around(_pointcut, func, *_args, **_kwargs)
        except:
            self.__logger.info("[Transaction] ROLLBACK")
            raise
        self.__logger.info("[Transaction] COMMIT")
        return result


@dataclass
class AsyncTransactional(AsyncPointcut):
    advice = AsyncTransactionalAdvice
