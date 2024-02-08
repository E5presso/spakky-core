from spakky.core.error import SpakkyCoreError


class SpakkyDomainError(SpakkyCoreError):
    ...


class DomainValidationError(SpakkyDomainError):
    ...
