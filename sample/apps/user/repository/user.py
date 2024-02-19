from uuid import UUID
from typing import Sequence

from sample.apps.user.domain.interface.repository.user import IAsyncUserRepository
from sample.apps.user.domain.model.user import User
from sample.common.aspects.logging import AsyncLogging
from spakky.domain.interfaces.repository import EntityNotFoundError
from spakky.stereotypes.repository import Repository


@Repository()
class AsyncInMemoryUserRepository(IAsyncUserRepository):
    database: dict[UUID, User]

    def __init__(self) -> None:
        super().__init__()
        self.database = {}

    @AsyncLogging()
    async def single(self, aggregate_id: UUID) -> User:
        try:
            return self.database[aggregate_id]
        except KeyError as e:
            raise EntityNotFoundError from e

    @AsyncLogging()
    async def single_or_none(self, aggregate_id: UUID) -> User | None:
        return self.database.get(aggregate_id, None)

    @AsyncLogging()
    async def get_by_username(self, username: str) -> User | None:
        return next(
            iter(x for x in self.database.values() if x.username == username), None
        )

    @AsyncLogging()
    async def contains(self, aggregate_id: UUID) -> bool:
        return aggregate_id in self.database

    @AsyncLogging()
    async def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[User]:
        return [user for id, user in self.database.items() if id in aggregate_ids]

    @AsyncLogging()
    async def save(self, aggregate: User) -> User:
        self.database[aggregate.uid] = aggregate
        return aggregate

    @AsyncLogging()
    async def save_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            self.database[aggregate.uid] = aggregate
        return aggregates

    @AsyncLogging()
    async def delete(self, aggregate: User) -> User:
        del self.database[aggregate.uid]
        return aggregate

    @AsyncLogging()
    async def delete_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            del self.database[aggregate.uid]
        return aggregates
