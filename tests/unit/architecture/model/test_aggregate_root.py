from uuid import UUID, uuid4
from typing import Self

from spakky.architecture.model.aggregate_root import IAggregateRoot
from spakky.architecture.model.domain_event import DomainEvent
from spakky.core.mutability import immutable, mutable


def test_aggregate_root_add_event() -> None:
    @mutable
    class User(IAggregateRoot[UUID]):
        name: str

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(id=uuid4(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)


def test_aggregate_root_remove_event() -> None:
    @mutable
    class User(IAggregateRoot[UUID]):
        name: str

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(id=uuid4(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)
    user.remove_event(user.events[0])
    assert len(user.events) == 0


def test_aggregate_root_clear_events() -> None:
    @mutable
    class User(IAggregateRoot[UUID]):
        name: str

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(id=uuid4(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)
    user.clear_events()
    assert len(user.events) == 0
