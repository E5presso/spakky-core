from uuid import UUID, uuid4
from typing import Self

from spakky.architecture.model.decorator import immutable, mutable
from spakky.architecture.model.domain_event import DomainEvent
from spakky.architecture.model.entity import Entity


def test_entity_equals() -> None:
    @mutable
    class User(Entity[UUID]):
        name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(id=uuid4(), name=name)

    user1: User = User(id=UUID("12345678-1234-5678-1234-567812345678"), name="John")
    user2: User = User(id=UUID("12345678-1234-5678-1234-567812345678"), name="Sarah")

    assert user1 == user2


def test_entity_not_equals_with_wrong_type() -> None:
    @mutable
    class User(Entity[UUID]):
        name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(id=uuid4(), name=name)

    @mutable
    class Class(Entity[UUID]):
        name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(id=uuid4(), name=name)

    user: User = User.create(name="John")
    clazz: Class = Class.create(name="first_class")

    assert user != clazz


def test_entity_not_equals() -> None:
    @mutable
    class User(Entity[UUID]):
        name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(id=uuid4(), name=name)

    user1: User = User.create(name="John")
    user2: User = User.create(name="John")

    assert user1 != user2


def test_entity_hash() -> None:
    @mutable
    class User(Entity[UUID]):
        name: str

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(id=uuid4(), name=name)

    user: User = User(id=UUID("12345678-1234-5678-1234-567812345678"), name="John")
    assert hash(user) == hash(UUID("12345678-1234-5678-1234-567812345678"))


def test_entity_add_event() -> None:
    @mutable
    class User(Entity[UUID]):
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


def test_entity_remove_event() -> None:
    @mutable
    class User(Entity[UUID]):
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


def test_entity_clear_events() -> None:
    @mutable
    class User(Entity[UUID]):
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
