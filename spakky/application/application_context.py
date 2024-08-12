from uuid import UUID, uuid4
from types import ModuleType
from typing import Any, Callable, Sequence, overload

from spakky.application.interfaces.container import (
    IContainer,
    NoSuchInjectableError,
    NoUniqueInjectableError,
)
from spakky.application.interfaces.pluggable import IPluggable, IRegistry
from spakky.application.interfaces.processor import IPostProcessor
from spakky.application.interfaces.registry import (
    CannotRegisterNonInjectableObjectError,
)
from spakky.core.importing import (
    Module,
    is_package,
    list_classes,
    list_functions,
    list_modules,
    resolve_module,
)
from spakky.core.types import AnyT
from spakky.injectable.injectable import Injectable, InjectableType, UnknownType
from spakky.injectable.primary import Primary


class ApplicationContext(IContainer, IRegistry):
    __target_type_map: dict[type, set[type]]
    __type_map: dict[type, UUID]
    __name_map: dict[str, UUID]
    __injectable_map: dict[UUID, InjectableType]
    __singleton_cache: dict[UUID, object]
    __post_processors: list[IPostProcessor]

    @property
    def injectables(self) -> set[InjectableType]:
        return set(self.__injectable_map.values())

    @property
    def post_processors(self) -> set[type[IPostProcessor]]:
        return {type(post_processor) for post_processor in self.__post_processors}

    def __init__(self, package: Module | set[Module] | None = None) -> None:
        self.__injectable_map = {}
        self.__target_type_map = {}
        self.__type_map = {}
        self.__name_map = {}
        self.__singleton_cache = {}
        self.__post_processors = []
        if package is None:
            return
        if isinstance(package, set):
            for package_item in package:
                self.scan(package_item)
            return
        self.scan(package)

    def __set_target_type(self, target_type: type) -> None:
        for base_type in target_type.mro():
            if base_type not in self.__target_type_map:
                self.__target_type_map[base_type] = set()
            self.__target_type_map[base_type].add(target_type)

    def __set_injectable(self, injectable: InjectableType) -> UUID:
        annotation: Injectable = Injectable.get(injectable)
        injectable_id: UUID = uuid4()
        self.__type_map[annotation.type_] = injectable_id
        self.__name_map[annotation.name] = injectable_id
        self.__injectable_map[injectable_id] = injectable
        return injectable_id

    def __get_target_type(self, required_type: type) -> type:
        if required_type not in self.__target_type_map:
            raise NoSuchInjectableError(required_type)
        derived: set[type] = self.__target_type_map[required_type]
        if len(derived) > 1:
            marked_as_primary: set[type] = {x for x in derived if Primary.contains(x)}
            if len(marked_as_primary) != 1:
                raise NoUniqueInjectableError(required_type, derived, marked_as_primary)
            derived = marked_as_primary
        return list(derived)[0]

    def __get_injectable_id_by_type(self, injectable_type: type) -> UUID:
        return self.__type_map[injectable_type]

    def __get_injectable_id_by_name(self, injectable_name: str) -> UUID:
        if injectable_name not in self.__name_map:
            raise NoSuchInjectableError(injectable_name)
        return self.__name_map[injectable_name]

    def __get_dependencies(self, injectable_type: InjectableType) -> dict[str, object]:
        annotation: Injectable = Injectable.get(injectable_type)
        dependencies: dict[str, object] = {}
        for name, required_type in annotation.dependencies.items():
            if required_type == UnknownType:
                dependencies[name] = self.__retrieve_injectable_by_name(name)
                continue
            dependencies[name] = self.__retrieve_injectable_by_type(required_type)
        return dependencies

    def __get_injectable_by_id(self, injectable_id: UUID) -> object:
        if injectable_id not in self.__singleton_cache:
            injectable = self.__instaniate_injectable(injectable_id)
            injectable = self.__post_process_injectable(injectable)
            self.__singleton_cache[injectable_id] = injectable
        return self.__singleton_cache[injectable_id]

    def __instaniate_injectable(self, injectable_id: UUID) -> object:
        injectable = self.__injectable_map[injectable_id]
        instance = injectable(**self.__get_dependencies(injectable))
        return instance

    def __post_process_injectable(self, injectable: object) -> object:
        for post_processor in self.__post_processors:
            injectable = post_processor.post_process(self, injectable)
        return injectable

    def __retrieve_injectable_by_type(self, injectable_type: type) -> object:
        actual_type = self.__get_target_type(injectable_type)
        injectable_id = self.__get_injectable_id_by_type(actual_type)
        return self.__get_injectable_by_id(injectable_id)

    def __retrieve_injectable_by_name(self, name: str) -> object:
        injectable_id = self.__get_injectable_id_by_name(name)
        return self.__get_injectable_by_id(injectable_id)

    @overload
    def contains(self, *, type_: type) -> bool: ...

    @overload
    def contains(self, *, name: str) -> bool: ...

    @overload
    def get(self, *, type_: type[AnyT]) -> AnyT: ...

    @overload
    def get(self, *, name: str) -> Any: ...

    def contains(
        self,
        type_: type | None = None,
        name: str | None = None,
    ) -> bool:
        if type_ is not None:
            if type_ not in self.__target_type_map:
                return False
            injectable_type = self.__get_target_type(type_)
            return injectable_type in self.__type_map
        if name is not None:
            return name in self.__name_map
        raise ValueError(
            "'name' and 'required_type' both cannot be None"
        )  # pragma: no cover

    def get(self, type_: type[AnyT] | None = None, name: str | None = None) -> AnyT | Any:
        if type_ is not None:
            return self.__retrieve_injectable_by_type(type_)
        if name is not None:
            return self.__retrieve_injectable_by_name(name)
        raise ValueError(
            "'name' and 'required_type' both cannot be None"
        )  # pragma: no cover

    def filter_injectable_types(self, clause: Callable[[type], bool]) -> Sequence[type]:
        return [x for x in self.__type_map if clause(x)]

    def filter_injectables(self, clause: Callable[[type], bool]) -> Sequence[object]:
        filtered: list[type[object]] = [x for x in self.__type_map if clause(x)]
        return [self.get(type_=x) for x in filtered]

    def register_injectable(self, injectable: InjectableType) -> None:
        if not Injectable.contains(injectable):
            raise CannotRegisterNonInjectableObjectError(injectable)
        annotation: Injectable = Injectable.get(injectable)
        self.__set_target_type(annotation.type_)
        self.__set_injectable(injectable)

    def register_post_processor(self, post_processor: IPostProcessor) -> None:
        self.__post_processors.append(post_processor)

    def register_plugin(self, pluggable: IPluggable) -> None:
        pluggable.register(self)

    def scan(self, package: Module) -> None:
        modules: set[ModuleType]

        if is_package(package):
            modules = list_modules(package)
        else:
            modules = {resolve_module(package)}

        for module in modules:
            injectables: set[type] = list_classes(module, Injectable.contains)
            factories: set[InjectableType] = list_functions(module, Injectable.contains)
            for injectable in injectables:
                self.register_injectable(injectable)
            for factory in factories:
                self.register_injectable(factory)

    def start(self) -> None:
        for injectable_id in self.__injectable_map:
            self.__get_injectable_by_id(injectable_id)
