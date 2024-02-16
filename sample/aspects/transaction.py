from typing import Callable, Awaitable
from dataclasses import dataclass

from spakky.aop.advisor import AsyncAdvisor, AsyncAspect, P, R
from spakky.aop.pointcut import AsyncPointcut
from spakky.core.generics import FuncT
from spakky.dependency.autowired import autowired
from spakky.domain.interfaces.unit_of_work import AbstractAsyncUnitOfWork


@AsyncAspect()
class AsyncTransactionalAdvisor(AsyncAdvisor):
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
    advisor = AsyncTransactionalAdvisor


def async_transactional(obj: FuncT) -> FuncT:
    return AsyncTransactional()(obj)
