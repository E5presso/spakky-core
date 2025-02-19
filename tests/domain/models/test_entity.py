import sys
from uuid import UUID, uuid4

import pytest

from spakky.core.mutability import mutable
from spakky.domain.error import AbstractDomainValidationError
from spakky.domain.models.entity import AbstractEntity, CannotMonkeyPatchEntityError

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


def test_entity_equals() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=uuid4(), name=name)

    user1: User = User(uid=UUID("12345678-1234-5678-1234-567812345678"), name="John")
    user2: User = User(uid=UUID("12345678-1234-5678-1234-567812345678"), name="Sarah")

    assert user1 == user2


def test_entity_not_equals_with_wrong_type() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    @mutable
    class Class(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user: User = User.create(name="John")
    clazz: Class = Class.create(name="first_class")

    assert user != clazz


def test_entity_not_equals_transient() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user1: User = User.create(name="John")
    user2: User = User.create(name="John")

    assert user1 != user2


def test_entity_not_equals() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user1: User = User.create(name="John")
    user2: User = User.create(name="John")

    assert user1 != user2


def test_entity_hash() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user: User = User(uid=UUID("12345678-1234-5678-1234-567812345678"), name="John")
    assert hash(user) == hash(UUID("12345678-1234-5678-1234-567812345678"))


def test_entity_prevent_monkey_patching() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            return

        def update_name(self, name: str) -> None:
            self.name = name

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls: type[Self], name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user: User = User.create(name="John")
    user.update_name("Sarah")

    assert user.name == "Sarah"
    with pytest.raises(CannotMonkeyPatchEntityError):
        user.update_name = lambda name: print(name)  # pylint: disable=unnecessary-lambda


def test_entity_validation_pass() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str
        age: int

        def validate(self) -> None:
            if not len(self.name) < 4:
                raise AbstractDomainValidationError
            if not 0 < self.age and self.age < 100:
                raise AbstractDomainValidationError

        def update_name(self, name: str) -> None:
            self.name = name

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls, name: str, age: int) -> Self:
            return cls(uid=cls.next_id(), name=name, age=age)

    @mutable
    class Class(AbstractEntity[UUID]):
        name: str

        def validate(self) -> None:
            if not len(self.name) < 10:
                raise AbstractDomainValidationError

        def update_name(self, name: str) -> None:
            self.name = name

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls, name: str) -> Self:
            return cls(uid=cls.next_id(), name=name)

    user: User = User.create("Sam", 30)
    clazz: Class = Class.create("Astronomy")
    with pytest.raises(AbstractDomainValidationError):
        user.update_name("John")
        clazz.update_name("Neuro-Science")
    with pytest.raises(AbstractDomainValidationError):
        User.create("Sarah", 10)
    with pytest.raises(AbstractDomainValidationError):
        User.create("Jesus", -1)
    with pytest.raises(AbstractDomainValidationError):
        User.create("Chris", 101)


def test_entity_attribute_will_not_change_if_validation_error_raised() -> None:
    @mutable
    class User(AbstractEntity[UUID]):
        name: str
        age: int

        def validate(self) -> None:
            if not len(self.name) < 4:
                raise AbstractDomainValidationError
            if not 0 < self.age and self.age < 100:
                raise AbstractDomainValidationError

        def update_name(self, name: str) -> None:
            self.name = name

        @classmethod
        def next_id(cls) -> UUID:
            return uuid4()

        @classmethod
        def create(cls, name: str, age: int) -> Self:
            return cls(uid=cls.next_id(), name=name, age=age)

    user: User = User.create("Sam", 30)
    with pytest.raises(AbstractDomainValidationError):
        user.update_name("John")
    assert user.name == "Sam"
