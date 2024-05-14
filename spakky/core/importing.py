import inspect
import pkgutil
import importlib
from types import ModuleType, FunctionType
from typing import Callable

from spakky.core.error import SpakkyCoreError


class CannotScanNonPackageModuleError(SpakkyCoreError):
    message = "Module that you specified is not a package module."


def list_modules(package: str | ModuleType) -> set[ModuleType]:
    if isinstance(package, str):
        package = importlib.import_module(package)
    if not hasattr(package, "__path__"):
        raise CannotScanNonPackageModuleError(package)
    modules: set[ModuleType] = set()
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if name.startswith("src."):
            name = name.removeprefix("src.")  # pragma: no cover
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
