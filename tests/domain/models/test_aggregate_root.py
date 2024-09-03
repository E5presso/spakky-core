import sys
from uuid import UUID, uuid4

from spakky.core.mutability import immutable, mutable
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.event import IntegrationEvent

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def test_aggregate_root_add_event() -> None:
    @mutable
    class User(AggregateRoot[UUID]):
        name: str

        def validate(self) -> None:
            return

        @immutable
        class Created(IntegrationEvent):
            name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

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

        def validate(self) -> None:
            return

        @immutable
        class Created(IntegrationEvent):
            name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

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

        def validate(self) -> None:
            return

        @immutable
        class Created(IntegrationEvent):
            name: str

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

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
