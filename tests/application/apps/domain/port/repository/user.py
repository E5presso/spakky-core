from typing import Protocol, runtime_checkable
from uuid import UUID

from spakky.domain.ports.persistency.repository import IGenericRepository
from tests.application.apps.domain.model.user import User


@runtime_checkable
class IUserRepository(IGenericRepository[User, UUID], Protocol): ...
