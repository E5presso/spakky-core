from uuid import UUID, uuid4
from typing import Self

from spakky.core.mutability import mutable
from spakky.domain.models.entity import Entity


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
