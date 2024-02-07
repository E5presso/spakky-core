from spakky.core.error import SpakkyCoreError


class SpakkyDomainError(SpakkyCoreError):
    ...


class ValidationFailedError(SpakkyDomainError):
    ...
