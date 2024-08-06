import inspect
import pkgutil
import importlib
from types import ModuleType, FunctionType
from typing import Callable, TypeAlias

from spakky.core.error import SpakkyCoreError

PATH = "__path__"
SRC_PREFIX = "src."
Module: TypeAlias = ModuleType | str


class CannotScanNonPackageModuleError(SpakkyCoreError):
    message = "Module that you specified is not a package module."


def resolve_module(module: Module) -> ModuleType:
    if not isinstance(module, str):
        return module
    return importlib.import_module(module)


def is_package(module: Module) -> bool:
    module = resolve_module(module)
    return hasattr(module, PATH)


def list_modules(package: Module) -> set[ModuleType]:
    package = resolve_module(package)
    if not is_package(package):
        raise CannotScanNonPackageModuleError(package)
    modules: set[ModuleType] = set()
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if name.startswith(SRC_PREFIX):
            name = name.removeprefix(SRC_PREFIX)  # pragma: no cover
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


def list_functions(
    module: ModuleType, selector: Callable[[FunctionType], bool] | None = None
) -> set[FunctionType]:
    if selector is None:
        return {member for _, member in inspect.getmembers(module, inspect.isfunction)}
    return {
        member
        for _, member in inspect.getmembers(module, inspect.isfunction)
        if selector(member)
    }
