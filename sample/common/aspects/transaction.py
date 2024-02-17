from typing import Callable, Awaitable
from dataclasses import dataclass

from spakky.aop.advice import Aspect, AsyncAdvice, AsyncPointcut, P, R
from spakky.core.generics import FuncT
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.unit_of_work import AbstractAsyncUnitOfWork


@Aspect()
class AsyncTransactionalAdvice(AsyncAdvice):
    __transacntion: AbstractAsyncUnitOfWork

    @autowired
    def __init__(self, transaction: AbstractAsyncUnitOfWork) -> None:
        super().__init__()
        self.__transacntion = transaction

    async def around(
        self, func: Callable[P, Awaitable[R]], *_args: P.args, **_kwargs: P.kwargs
    ) -> R:
        async with self.__transacntion:
            return await super().around(func, *_args, **_kwargs)


@dataclass
class AsyncTransactional(AsyncPointcut):
    advice = AsyncTransactionalAdvice


def async_transactional(obj: FuncT) -> FuncT:
    return AsyncTransactional()(obj)
