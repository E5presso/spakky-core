from abc import ABC
from typing import ClassVar


class AbstractSpakkyCoreError(Exception, ABC):
    message: ClassVar[str]
