import inspect
import pkgutil
import importlib
from types import ModuleType, FunctionType
from typing import Any, Callable, TypeAlias
from fnmatch import filter

from spakky.core.error import SpakkyCoreError

PATH = "__path__"
SRC_PREFIX = "src."
Module: TypeAlias = ModuleType | str


class CannotScanNonPackageModuleError(SpakkyCoreError):
    message = "Module that you specified is not a package module."


def resolve_module(module: Module) -> ModuleType:
    if isinstance(module, str):
        return importlib.import_module(module)
    return module


def is_package(module: Module) -> bool:
    module = resolve_module(module)
    return hasattr(module, PATH)


def is_subpath_of(module: ModuleType, patterns: set[Module]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, str):
            if module.__name__ == pattern:
                return True
            if any(filter([module.__name__], pattern)):
                return True
            continue
        if module.__name__.startswith(pattern.__name__):
            return True
    return False


def list_modules(package: Module, exclude: set[Module] | None = None) -> set[ModuleType]:
    package = resolve_module(package)
    if not is_package(package):
        raise CannotScanNonPackageModuleError(package)
    if exclude is None:
        exclude = set()
    modules: set[ModuleType] = set()
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        if name.startswith(SRC_PREFIX):
            name = name.removeprefix(SRC_PREFIX)  # pragma: no cover
        module = importlib.import_module(name)
        if is_subpath_of(module, exclude):
            continue
        modules.add(module)
    return modules


def list_classes(
    module: ModuleType, selector: Callable[[type], bool] | None = None
) -> set[type]:
    if selector is not None:
        return {
            member
            for _, member in inspect.getmembers(
                module, lambda x: inspect.isclass(x) and selector(x)
            )
        }
    return {member for _, member in inspect.getmembers(module, inspect.isclass)}


def list_functions(
    module: ModuleType, selector: Callable[[FunctionType], bool] | None = None
) -> set[FunctionType]:
    if selector is not None:
        return {
            member
            for _, member in inspect.getmembers(
                module, lambda x: inspect.isfunction(x) and selector(x)
            )
        }
    return {member for _, member in inspect.getmembers(module, inspect.isfunction)}


def list_objects(
    module: ModuleType, selector: Callable[[Any], bool] | None = None
) -> set[FunctionType]:
    if selector is not None:
        return {
            member
            for _, member in inspect.getmembers(
                module,
                lambda x: (inspect.isclass(x) or inspect.isfunction(x)) and selector(x),
            )
        }
    return {
        member
        for _, member in inspect.getmembers(
            module, lambda x: inspect.isclass(x) or inspect.isfunction(x)
        )
    }
