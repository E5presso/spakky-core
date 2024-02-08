from uuid import UUID, uuid4
from typing import Self

from spakky.core.mutability import immutable, mutable
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


def test_aggregate_root_add_event() -> None:
    @mutable
    class User(AggregateRoot[UUID]):
        name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(uid=cls.next_id(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)


def test_aggregate_root_remove_event() -> None:
    @mutable
    class User(AggregateRoot[UUID]):
        name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(uid=cls.next_id(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)
    user.remove_event(user.events[0])
    assert len(user.events) == 0


def test_aggregate_root_clear_events() -> None:
    @mutable
    class User(AggregateRoot[UUID]):
        name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @immutable
        class Created(DomainEvent):
            name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            self: Self = cls(uid=cls.next_id(), name=name)
            self.add_event(self.Created(name=self.name))
            return self

    user: User = User.create(name="John")
    assert len(user.events) == 1
    assert isinstance(user.events[0], User.Created)
    user.clear_events()
    assert len(user.events) == 0
