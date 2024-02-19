from datetime import datetime
from dataclasses import field

from spakky.core.mutability import immutable
from spakky.domain.models.value_object import ValueObject


@immutable
class AuthenticationLog(ValueObject):
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str
    user_agent: str
