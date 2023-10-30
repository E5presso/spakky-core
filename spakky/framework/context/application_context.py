from types import ModuleType
from typing import Any, TypeVar

from spakky.framework.core.importing import get_full_class_path, get_module

from .stereotype.component import IComponent


T = TypeVar("T", bound=Any)
T_COMPONENT = TypeVar("T_COMPONENT", bound=IComponent)


class NoSuchComponentDefinitionException(Exception):
    __type: type

    def __init__(self, _type: type) -> None:
        self.__type = _type

    def __repr__(self) -> str:
        return f"No such component definition in ApplicationContext '{self.__type}'"


class NoUniqueComponentDefinitionException(Exception):
    __type: type

    def __init__(self, _type: type) -> None:
        self.__type = _type

    def __repr__(self) -> str:
        return f"No unique component definition in ApplicationContext '{self.__type}'"


class ApplicationContext:
    _types_map: dict[str, set[type[IComponent]]]
    _class_container: dict[str, type[IComponent]]
    _singleton_cache: dict[str, Any]
    _modules: set[ModuleType]

    def __init__(self) -> None:
        self._types_map = {}
        self._class_container = {}
        self._singleton_cache = {}
        self._modules = set()

    @property
    def components(self) -> list[str]:
        return list(self._class_container.keys())

    def register(self, component: type[T_COMPONENT]) -> None:
        bases: tuple[type, ...] = component.__bases__
        for base in bases:
            if get_full_class_path(base) not in self._types_map:
                self._types_map[get_full_class_path(base)] = set()
            self._types_map[get_full_class_path(base)].add(component)
        if get_full_class_path(component) not in self._types_map:
            self._types_map[get_full_class_path(component)] = {component}
        self._modules.add(get_module(component))
        self._class_container[get_full_class_path(component)] = component

    def wire(self, module: ModuleType) -> None:
        self._modules.add(module)

    def retrieve(self, _type: type[T]) -> T:
        type_key: str = get_full_class_path(_type)
        if type_key not in self._types_map:
            raise NoSuchComponentDefinitionException(_type)
        derived: set[type] = self._types_map[type_key]
        if len(derived) == 0:
            raise NoSuchComponentDefinitionException(_type)
        if len(derived) > 1:
            raise NoUniqueComponentDefinitionException(_type)
        target: type = list(derived)[0]
        target_key: str = get_full_class_path(target)
        if target_key not in self._singleton_cache:
            if target_key not in self._class_container:
                raise NoSuchComponentDefinitionException(target)
            component: type[IComponent] = self._class_container[target_key]
            autowired: dict[str, type] = component.__autowired__
            self._singleton_cache[target_key] = component(**{k: self.retrieve(t) for k, t in autowired.items()})
        return self._singleton_cache[target_key]
