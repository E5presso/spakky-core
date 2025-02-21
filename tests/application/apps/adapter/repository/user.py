from typing import Sequence
from uuid import UUID

from spakky.domain.ports.persistency.repository import EntityNotFoundError
from spakky.pod.annotations.pod import Pod
from tests.application.apps.domain.model.user import User
from tests.application.apps.domain.port.repository.user import IUserRepository


@Pod()
class UserRepository(IUserRepository):
    __memory: dict[UUID, User] = {}

    def __init__(self) -> None:
        self.__memory = {}

    def get(self, aggregate_id: UUID) -> User:
        try:
            return self.__memory[aggregate_id]
        except KeyError:
            raise EntityNotFoundError(aggregate_id)

    def get_or_none(self, aggregate_id: UUID) -> User | None:
        return self.__memory.get(aggregate_id)

    def contains(self, aggregate_id: UUID) -> bool:
        return aggregate_id in self.__memory

    def range(self, aggregate_ids: Sequence[UUID]) -> Sequence[User]:
        try:
            return [self.__memory[aggregate_id] for aggregate_id in aggregate_ids]
        except KeyError as e:
            raise EntityNotFoundError(aggregate_ids) from e

    def save(self, aggregate: User) -> User:
        self.__memory[aggregate.uid] = aggregate
        return aggregate

    def save_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            self.__memory[aggregate.uid] = aggregate
        return aggregates

    def delete(self, aggregate: User) -> User:
        del self.__memory[aggregate.uid]
        return aggregate

    def delete_all(self, aggregates: Sequence[User]) -> Sequence[User]:
        for aggregate in aggregates:
            del self.__memory[aggregate.uid]
        return aggregates
