from re import Pattern, compile
from uuid import UUID, uuid4
from typing import Self
from dataclasses import field

from spakky.core.mutability import immutable, mutable
from spakky.domain.error import DomainValidationError
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


class EmailValidationError(DomainValidationError):
    ...


@mutable
class User(AggregateRoot[UUID]):
    EMAIL_REGEX: Pattern[str] = field(
        init=False,
        default=compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ),
    )

    username: str
    password: str
    email: str

    @immutable
    class PasswordUpdated(DomainEvent):
        id: UUID

    @immutable
    class EmailUpdated(DomainEvent):
        id: UUID

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

    @classmethod
    def create(cls, username: str, password: str, email: str) -> Self:
        return cls(
            id=cls.next_id(),
            username=username,
            password=password,
            email=email,
        )

    def validate(self) -> None:
        if not self.EMAIL_REGEX.fullmatch(self.email):
            raise EmailValidationError

    def update_password(self, password: str) -> None:
        self.password = password
        self.add_event(self.PasswordUpdated(id=self.id))

    def update_email(self, email: str) -> None:
        self.email = email
        self.add_event(self.EmailUpdated(id=self.id))
