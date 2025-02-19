from abc import ABC

from spakky.core.error import AbstractSpakkyCoreError


class AbstractSpakkyDomainError(AbstractSpakkyCoreError, ABC): ...


class AbstractDomainValidationError(AbstractSpakkyDomainError, ABC): ...
