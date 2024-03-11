from abc import ABC


class SpakkyCoreError(Exception, ABC):
    message: str
