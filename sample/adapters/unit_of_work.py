from spakky.dependency.component import Component
from spakky.domain.interfaces.unit_of_work import AbstractAsyncUnitOfWork


@Component()
class AsyncMemoryUnitOfWork(AbstractAsyncUnitOfWork):
    async def initialize(self) -> None:
        ...

    async def dispose(self) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...
