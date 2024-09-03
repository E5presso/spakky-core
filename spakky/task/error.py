from spakky.core.error import SpakkyCoreError


class SpakkyTaskError(SpakkyCoreError): ...


class TaskAlreadyStartedError(SpakkyCoreError):
    message = "Task is already started"


class TaskNotStartedError(SpakkyCoreError):
    message = "Task is not started"
