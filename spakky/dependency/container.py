from typing import Any, Callable, Sequence, overload

from spakky.dependency.autowired import Unknown
from spakky.dependency.component import Component
from spakky.dependency.error import SpakkyComponentError
from spakky.dependency.primary import Primary
from spakky.dependency.provider import Provider, ProvidingType
from spakky.core.generics import ObjectT


class CannotRegisterNonComponentError(SpakkyComponentError):
    ...


class NoSuchComponentError(SpakkyComponentError):
    ...


class NoUniqueComponentError(SpakkyComponentError):
    ...


class ComponentContainer:
    __type_map: dict[type, set[type]]
    __components_type_map: dict[type, type]
    __components_name_map: dict[str, type]
    __components: list[type]
    __singleton_cache: dict[type, Any]

    def __init__(self) -> None:
        super().__init__()
        self.__type_map = {}
        self.__components_type_map = {}
        self.__components_name_map = {}
        self.__components = []
        self.__singleton_cache = {}

    def register(self, component: type) -> None:
        if not Component.contains(component):
            raise CannotRegisterNonComponentError
        component_annotation: Component = Component.single(component)
        for base in component.__mro__:
            if base not in self.__type_map:
                self.__type_map[base] = set()
            self.__type_map[base].add(component)
        self.__components_type_map[component] = component
        self.__components_name_map[component_annotation.name] = component
        self.__components.append(component)

    @overload
    def contains(self, *, required_type: type) -> bool:
        ...

    @overload
    def contains(self, *, name: str) -> bool:
        ...

    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool:
        if required_type is not None:
            return required_type in self.__components_type_map
        return name in self.__components_name_map

    def __get_target_type(self, required_type: type) -> type:
        if required_type not in self.__type_map:
            raise NoSuchComponentError(required_type)
        derived: set[type] = self.__type_map[required_type]
        if len(derived) > 1:
            marked_as_primary: set[type] = {x for x in derived if Primary.contains(x)}
            if len(marked_as_primary) != 1:
                raise NoUniqueComponentError(required_type)
            derived = marked_as_primary
        return list(derived)[0]

    def __get_instance(
        self, component: type[ObjectT], providing_type: ProvidingType
    ) -> ObjectT:
        component_annotation: Component = Component.single(component)
        dependencies: dict[str, Any] = {}
        for name, required_type in component_annotation.dependencies.items():
            if required_type == Unknown:
                dependencies[name] = self.get(name=name)
                continue
            dependencies[name] = self.get(required_type=required_type)
        if providing_type == ProvidingType.FACTORY:
            return component(**dependencies)
        if component not in self.__singleton_cache:
            self.__singleton_cache[component] = component(**dependencies)
            return self.__singleton_cache[component]
        return self.__singleton_cache[component]

    @overload
    def get(self, *, required_type: type[ObjectT]) -> ObjectT:
        ...

    @overload
    def get(self, *, name: str) -> object:
        ...

    def get(
        self, required_type: type[ObjectT] | None = None, name: str | None = None
    ) -> ObjectT | object:
        if required_type is not None:
            target: type = self.__get_target_type(required_type)
            component: type = self.__components_type_map[target]
            provider_annotation: Provider | None = Provider.single_or_none(component)
            providing_type: ProvidingType = (
                provider_annotation.providing_type
                if provider_annotation is not None
                else ProvidingType.SINGLETON
            )
            return self.__get_instance(component=component, providing_type=providing_type)
        if name not in self.__components_name_map:
            raise NoSuchComponentError(name)
        component: type = self.__components_name_map[name]
        provider_annotation: Provider | None = Provider.single_or_none(component)
        providing_type: ProvidingType = (
            provider_annotation.providing_type
            if provider_annotation is not None
            else ProvidingType.SINGLETON
        )
        return self.__get_instance(component=component, providing_type=providing_type)

    def where(self, clause: Callable[[type], bool]) -> Sequence[object]:
        return [
            self.__get_instance(
                x,
                Provider.single(x).providing_type
                if Provider.contains(x)
                else ProvidingType.SINGLETON,
            )
            for x in self.__components
            if clause(x)
        ]
