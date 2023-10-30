from types import ModuleType
from typing import Any, Protocol, runtime_checkable
from spakky.framework.context.application_context import ApplicationContext
from spakky.framework.context.stereotype.component import IComponent
from spakky.framework.core.generic import T_CLASS
from spakky.framework.core.importing import full_scan_modules, get_module, list_classes


class CannotScanCurrentModuleException(Exception):
    def __repr__(self) -> str:
        return f"Cannot scan current module"


@runtime_checkable
class IComponentScan(Protocol):
    __context__: ApplicationContext

    def __instancecheck__(self, __instance: Any) -> bool:
        return hasattr(__instance, "__context__")

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return hasattr(__subclass, "__context__")


class ComponentScan:
    _base_packages: list[str]

    def __init__(self, base_packages: list[str] | str = []) -> None:
        if isinstance(base_packages, str):
            base_packages = [base_packages]
        self._base_packages = base_packages

    def __call__(self, cls: T_CLASS) -> T_CLASS:
        current_path: str | None = get_module(cls).__file__
        if current_path is None:
            raise CannotScanCurrentModuleException
        modules: set[ModuleType] = full_scan_modules([current_path] + self._base_packages)
        components: set[type[IComponent]] = set()
        for module in modules:
            [components.add(x) for x in list_classes(module, lambda x: issubclass(x, IComponent))]
        context: ApplicationContext = ApplicationContext()
        [context.register(x) for x in components]
        setattr(cls, "__context__", context)
        return cls
