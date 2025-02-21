import sys
from uuid import UUID, uuid4

from spakky.core.mutability import mutable
from spakky.domain.models.aggregate_root import AbstractAggregateRoot

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


@mutable
class User(AbstractAggregateRoot[UUID]):
    email: str
    password: str
    username: str

    @classmethod
    def next_id(cls) -> UUID:
        return uuid4()

    def validate(self) -> None:
        return

    @classmethod
    def create(cls, email: str, password: str, username: str) -> Self:
        return cls(
            uid=cls.next_id(),
            email=email,
            password=password,
            username=username,
        )

    def update_email(self, email: str) -> None:
        self.email = email

    def update_password(self, password: str) -> None:
        self.password = password

    def update_username(self, username: str) -> None:
        self.username = username
