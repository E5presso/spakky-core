from abc import ABC

from spakky.core.error import SpakkyCoreError


class SpakkyDomainError(SpakkyCoreError, ABC): ...


class DomainValidationError(SpakkyDomainError, ABC): ...
