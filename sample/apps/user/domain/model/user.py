from re import Pattern, compile
from uuid import UUID, uuid4
from typing import Self, ClassVar
from dataclasses import field

from sample.apps.user.domain.error import (
    AuthenticationFailedError,
    EmailValidationFailedError,
)
from sample.apps.user.domain.model.authentication_log import AuthenticationLog
from spakky.core.mutability import immutable, mutable
from spakky.cryptography.password import Password
from spakky.domain.models.aggregate_root import AggregateRoot
from spakky.domain.models.domain_event import DomainEvent


@mutable
class User(AggregateRoot[UUID]):
    EMAIL_REGEX: ClassVar[Pattern[str]] = field(
        init=False,
        default=compile(
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        ),
    )

    username: str
    password: str
    email: str
    authentication_logs: list[AuthenticationLog] = field(
        default_factory=list[AuthenticationLog]
    )

    @immutable
    class Created(DomainEvent):
        uid: UUID

    @immutable
    class PasswordUpdated(DomainEvent):
        uid: UUID

    @immutable
    class EmailUpdated(DomainEvent):
        uid: UUID

    @immutable
    class Authenticated(DomainEvent):
        uid: UUID
        ip_address: str
        user_agent: str

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

    @classmethod
    def create(cls: type[Self], username: str, password: str, email: str) -> Self:
        self: Self = cls(
            uid=cls.next_id(),
            username=username,
            password=Password(password=password).export,
            email=email,
        )
        self.add_event(cls.Created(uid=self.uid))
        return self

    def validate(self) -> None:
        if not self.EMAIL_REGEX.fullmatch(self.email):
            raise EmailValidationFailedError

    def update_password(self, old: str, new: str) -> None:
        if not Password(password_hash=self.password).challenge(old):
            raise AuthenticationFailedError
        self.password = Password(password=new).export
        self.add_event(self.PasswordUpdated(uid=self.uid))

    def update_email(self, email: str) -> None:
        self.email = email
        self.add_event(self.EmailUpdated(uid=self.uid))

    def authenticate(self, password: str, ip_address: str, user_agent: str) -> None:
        if not Password(password_hash=self.password).challenge(password):
            raise AuthenticationFailedError
        self.authentication_logs.append(
            AuthenticationLog(ip_address=ip_address, user_agent=user_agent)
        )
        self.add_event(
            self.Authenticated(uid=self.uid, ip_address=ip_address, user_agent=user_agent)
        )
