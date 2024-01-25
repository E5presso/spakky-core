import inspect
import pkgutil
import importlib
from types import ModuleType
from typing import Callable

from spakky.core.error import SpakkyCoreError


class CannotScanNonPackageModuleError(SpakkyCoreError):
    __module: ModuleType

    def __init__(self, module: ModuleType) -> None:
        self.__module = module

    def __repr__(self) -> str:
        return f"'{self.__module.__name__}' is not a package module."


def list_modules(package: ModuleType) -> set[ModuleType]:
    if not hasattr(package, "__path__"):
        raise CannotScanNonPackageModuleError(package)
    modules: set[ModuleType] = set()
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        modules.add(importlib.import_module(name))
    return modules


def list_classes(
    module: ModuleType, selector: Callable[[type], bool] | None = None
) -> set[type]:
    if selector is None:
        return {member for _, member in inspect.getmembers(module, inspect.isclass)}
    return {
        member
        for _, member in inspect.getmembers(module, inspect.isclass)
        if selector(member)
    }
