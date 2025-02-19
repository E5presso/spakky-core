from abc import ABC


class AbstractSpakkyCoreError(Exception, ABC):
    message: str
