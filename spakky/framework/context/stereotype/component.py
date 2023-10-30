from typing import Any, Callable, Protocol, runtime_checkable

from spakky.framework.core.generic import T_CLASS


@runtime_checkable
class IComponent(Protocol):
    __autowired__: dict[str, type]

    def __instancecheck__(self, __instance: Any) -> bool:
        return hasattr(__instance, "__autowired__")

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return hasattr(__subclass, "__autowired__")


class Component:
    def __call__(self, cls: T_CLASS) -> T_CLASS:
        constructor: Callable[..., None] = cls.__init__
        autowired: dict[str, type] = getattr(constructor, "__autowired__", {})
        setattr(cls, "__autowired__", autowired)
        return cls
