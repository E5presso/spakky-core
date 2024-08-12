from abc import abstractmethod
from typing import Protocol, runtime_checkable

from spakky.application.interfaces.processor import IPostProcessor
from spakky.injectable.injectable import InjectableType
from spakky.injectable.error import SpakkyInjectableError


class CannotRegisterNonInjectableObjectError(SpakkyInjectableError):
    message = "Cannot register non-injectable object."


@runtime_checkable
class IRegistry(Protocol):
    @abstractmethod
    def register_injectable(self, injectable: InjectableType) -> None: ...

    @abstractmethod
    def register_post_processor(self, post_processor: IPostProcessor) -> None: ...
