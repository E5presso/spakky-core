import importlib
import inspect
import pkgutil
from fnmatch import filter
from types import FunctionType, ModuleType
from typing import Any, Callable, TypeAlias

from spakky.core.constants import PATH
from spakky.core.error import AbstractSpakkyCoreError

Module: TypeAlias = ModuleType | str


class CannotScanNonPackageModuleError(AbstractSpakkyCoreError):
    message = "Module that you specified is not a package module."


def resolve_module(module: Module) -> ModuleType:
    if isinstance(module, str):
        try:
            return importlib.import_module(module)
        except ImportError as e:
            raise ImportError(f"Failed to import module '{module}': {e}") from e
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


def list_modules(
    package: Module, exclude: set[Module] | None = None
) -> set[ModuleType]:
    package = resolve_module(package)
    if not is_package(package):
        raise CannotScanNonPackageModuleError(package)
    if exclude is None:
        exclude = set()
    modules: set[ModuleType] = set()
    for _, name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = importlib.import_module(name)
        except ImportError:
            continue
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
