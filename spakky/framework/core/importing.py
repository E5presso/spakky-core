import os
import inspect
import importlib
from types import ModuleType
from typing import Callable


class ModulePathNotFoundException(Exception):
    __path: str

    def __init__(self, path: str) -> None:
        self.__path = path

    def __repr__(self) -> str:
        return f"Module path not found '{self.__path}'"

    def __str__(self) -> str:
        return self.__repr__()


def get_full_class_path(cls: type) -> str:
    return f"{cls.__module__}.{cls.__name__}"


def full_scan_modules(path: list[str]) -> set[ModuleType]:
    module_paths: set[ModuleType] = set()
    for base_package in path:
        package: str = base_package
        directory, extension = os.path.splitext(package)
        package = directory.replace(".", os.path.sep) + extension
        if not os.path.exists(package):
            raise ModulePathNotFoundException(package)
        if os.path.isfile(package):
            module_path: str = os.path.splitext(package)[0]
            module_path = os.path.relpath(module_path)
            package = os.path.sep.join(module_path.split(os.path.sep)[:-1])
        for dir, _, files in os.walk(package):
            if any(
                [x for x in dir.split(os.path.sep) if x != os.path.curdir and (x.startswith(".") or x.startswith("__"))]
            ):
                continue
            for file in files:
                name, extension = os.path.splitext(file)
                if extension != ".py":
                    continue
                if name.startswith("__"):
                    continue
                module_path: str = os.path.splitext(os.path.join(dir, file))[0]
                if module_path.split(os.path.sep)[0] == os.path.curdir:
                    module_path = module_path[len(os.path.curdir) :].lstrip(os.path.sep)
                module_path = module_path.replace(os.path.sep, ".")
                module_paths.add(importlib.import_module(module_path))
    return module_paths


def list_classes(module: ModuleType, selector: Callable[[type], bool] | None = None) -> list[type]:
    classes: list[type] = []
    for _, member in inspect.getmembers(module):
        if not inspect.isclass(member):
            continue
        if selector is None:
            classes.append(member)
            continue
        if selector(member):
            classes.append(member)
    return classes


def get_module(obj: object) -> ModuleType:
    return importlib.import_module(obj.__module__)
