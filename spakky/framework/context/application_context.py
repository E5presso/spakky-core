from types import ModuleType
from typing import Any, TypeVar

from spakky.framework.core.importing import get_full_class_path, get_module

from .stereotype.component import Component


T = TypeVar("T", bound=Any)


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
    type_map: dict[str, set[type]]
    class_container: dict[str, type]
    singleton_cache: dict[str, Any]

    def __init__(self) -> None:
        self.type_map = {}
        self.class_container = {}
        self.singleton_cache = {}

    @property
    def components(self) -> list[str]:
        return list(self.class_container.keys())

    def register(self, component: type) -> None:
        bases: tuple[type, ...] = component.__bases__
        for base in bases:
            if get_full_class_path(base) not in self.type_map:
                self.type_map[get_full_class_path(base)] = set()
            self.type_map[get_full_class_path(base)].add(component)
        if get_full_class_path(component) not in self.type_map:
            self.type_map[get_full_class_path(component)] = {component}
        self.class_container[get_full_class_path(component)] = component

    def retrieve(self, _type: type[T]) -> T:
        type_key: str = get_full_class_path(_type)
        if type_key not in self.type_map:
            raise NoSuchComponentDefinitionException(_type)
        derived: set[type] = self.type_map[type_key]
        if len(derived) == 0:
            raise NoSuchComponentDefinitionException(_type)
        if len(derived) > 1:
            raise NoUniqueComponentDefinitionException(_type)
        target: type = list(derived)[0]
        target_key: str = get_full_class_path(target)
        if target_key not in self.singleton_cache:
            if target_key not in self.class_container:
                raise NoSuchComponentDefinitionException(target)
            component: type = self.class_container[target_key]
            annotation: Component | None = Component.get_annotation(component)
            if annotation is None:
                raise NoSuchComponentDefinitionException(component)
            autowired: dict[str, type] = annotation.autowired
            self.singleton_cache[target_key] = component(**{k: self.retrieve(t) for k, t in autowired.items()})
        return self.singleton_cache[target_key]
