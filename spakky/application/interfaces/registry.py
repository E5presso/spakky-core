from typing import Protocol, runtime_checkable

from spakky.application.interfaces.bean_processor_registry import (
    IBeanPostProcessorRegistry,
)
from spakky.application.interfaces.bean_registry import IBeanRegistry


@runtime_checkable
class IRegistry(IBeanRegistry, IBeanPostProcessorRegistry, Protocol): ...
