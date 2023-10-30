from typing import Any, Protocol, runtime_checkable

from spakky.framework.core.generic import T_CLASS

from .component import Component, IComponent


@runtime_checkable
class IConfiguration(IComponent, Protocol):
    __configuration__: bool

    def __instancecheck__(self, __instance: Any) -> bool:
        return super().__instancecheck__(__instance) and hasattr(__instance, "__configuration__")

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return super().__subclasshook__(__subclass) and hasattr(__subclass, "__configuration__")


class Configuration(Component):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, cls: T_CLASS) -> T_CLASS:
        cls = super().__call__(cls)
        setattr(cls, "__configuration__", True)
        return cls
