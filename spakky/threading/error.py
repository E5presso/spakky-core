from spakky.core.error import SpakkyCoreError


class SpakkyThreadingError(SpakkyCoreError): ...


class ThreadAlreadyStartedError(SpakkyCoreError):
    message = "Thread is already started"


class ThreadNotStartedError(SpakkyCoreError):
    message = "Thread is not started"
