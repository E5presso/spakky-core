from uuid import UUID
from typing import Sequence

from sample.user.domain.interface.repository.user import IAsyncUserRepository
from sample.user.domain.model.user import User
from spakky.stereotypes.repository import Repository


@Repository()
class AsyncMemoryUserRepository(IAsyncUserRepository):
    database: dict[UUID, User]

    def __init__(self) -> None:
        super().__init__()
        self.database = {}

    async def single(self, aggregate_id: UUID) -> User:
        return self.database[aggregate_id]

    async def single_or_none(self, aggregate_id: UUID) -> User | None:
        return self.database.get(aggregate_id, None)

    async def contains(self, aggregate_id: UUID) -> bool:
        return aggregate_id in self.database

    async def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[User]:
        return [user for id, user in self.database.items() if id in aggregate_ids]

    async def save(self, aggregate: User) -> User:
        self.database[aggregate.uid] = aggregate
        return aggregate

    async def save_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            self.database[aggregate.uid] = aggregate
        return aggregates

    async def delete(self, aggregate: User) -> User:
        del self.database[aggregate.uid]
        return aggregate

    async def delete_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            del self.database[aggregate.uid]
        return aggregates
