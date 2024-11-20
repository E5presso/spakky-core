import sys
from copy import deepcopy
from uuid import UUID
from types import ModuleType, GenericAlias
from typing import Callable, cast, get_args, get_origin

from spakky.application.error import SpakkyApplicationError
from spakky.application.interfaces.container import (
    IPodContainer,
    NoSuchPodError,
    NoUniquePodError,
)
from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.plugin_registry import IPluginRegistry
from spakky.application.interfaces.post_processor import IPodPostProcessor
from spakky.application.interfaces.registry import (
    CannotRegisterNonPodObjectError,
    IPodRegistry,
)
from spakky.core.importing import (
    Module,
    is_package,
    list_modules,
    list_objects,
    resolve_module,
)
from spakky.core.mro import generic_mro
from spakky.core.types import ObjectT, is_optional
from spakky.pod.lazy import Lazy
from spakky.pod.order import Order
from spakky.pod.pod import Pod, PodType
from spakky.pod.primary import Primary


class CircularDependencyGraphDetectedError(SpakkyApplicationError):
    message = "Circular dependency detected"


class ApplicationContext(IPodContainer, IPodRegistry, IPluginRegistry):
    __forward_type_map: dict[str, type]
    __type_lookup: dict[type, set[type]]  # {base: {derived}}
    __pods: set[Pod]
    __singleton_cache: dict[UUID, object]
    __post_processors: list[IPodPostProcessor]

    @property
    def pods(self) -> set[PodType]:
        return {x.target for x in self.__pods}

    @property
    def post_processors(self) -> set[type[IPodPostProcessor]]:
        return {type(x) for x in self.__post_processors}

    def __init__(
        self,
        package: Module | set[Module] | None = None,
        exclude: set[Module] | None = None,
    ) -> None:
        self.__forward_type_map = {}
        self.__type_lookup = {}
        self.__pods = set()
        self.__singleton_cache = {}
        self.__post_processors = []
        if package is None:
            return
        if exclude is None:
            exclude = set()
        if isinstance(package, set):
            for package_item in package:
                self.scan(package_item, exclude)
            return
        self.scan(package, exclude)

    def __register_pod_definition(self, pod: Pod) -> None:
        for base_type in generic_mro(pod.type_):
            if base_type not in self.__type_lookup:
                self.__type_lookup[base_type] = set()
            self.__type_lookup[base_type].add(pod.type_)
        self.__forward_type_map[pod.type_.__name__] = pod.type_
        self.__pods.add(pod)

    def __resolve_single_type_or_none(self, type_: type, name: str | None) -> type | None:
        if type_ not in self.__type_lookup:
            return None
        derived = self.__type_lookup[type_].copy()
        if len(derived) == 1:
            return derived.pop()
        uniquified = {x for x in derived if Primary.exists(x) or Pod.get(x).name == name}
        if len(uniquified) != 1:
            raise NoUniquePodError(type_, name)
        return uniquified.pop()

    def __resolve_all_types(self, type_: type) -> set[type] | None:
        if type_ not in self.__type_lookup:
            return None
        return self.__type_lookup[type_].copy()

    def __post_process_pod(self, pod: object) -> object:
        for post_processor in self.__post_processors:
            pod = post_processor.post_process(self, pod)
        return pod

    def __create_pod_instance(self, pod: Pod, dependency_hierarchy: list[type]) -> object:
        if pod.scope == Pod.Scope.SINGLETON and pod.id in self.__singleton_cache:
            return self.__singleton_cache[pod.id]
        dependencies: dict[str, object] = {
            name: self.__get_internal(
                dependency.type_,
                name,
                deepcopy(dependency_hierarchy),  # Copy to avoid mutation
            )
            for name, dependency in pod.dependencies.items()
            if not dependency.has_default
        }
        instance: object = pod.target(**dependencies)
        processed: object = self.__post_process_pod(instance)
        if pod.scope == Pod.Scope.SINGLETON:
            self.__singleton_cache[pod.id] = processed
        return processed

    def __get_instance_by_type(
        self,
        type_: type,
        name: str | None,
        resolved_type: type,
        dependency_hierarchy: list[type],
    ) -> tuple[str, object]:
        pods: set[Pod] = {x for x in self.__pods if x.type_ == resolved_type}
        if len(pods) > 1:
            if name is None:
                raise NoUniquePodError(resolved_type, name)
            pods = {x for x in pods if x.name == name}
        if len(pods) == 0:
            raise NoSuchPodError(resolved_type, name)
        pod: Pod = pods.pop()
        dependency_hierarchy.append(type_)
        return pod.name, self.__create_pod_instance(pod, dependency_hierarchy)

    def __get_internal_as_list(
        self,
        type_: GenericAlias,
        name: str | None,
        dependency_hierarchy: list[type],
    ) -> list[object] | None:
        target_type = get_args(type_)[0]
        resolved_types = self.__resolve_all_types(target_type)
        if resolved_types is None:
            if is_optional(type_):
                return None
            raise NoSuchPodError(type_)
        return [
            instance
            for _, instance in [
                self.__get_instance_by_type(
                    resolved_type,
                    name,
                    resolved_type,
                    dependency_hierarchy,
                )
                for resolved_type in resolved_types
            ]
        ]

    def __get_internal_as_set(
        self,
        type_: GenericAlias,
        name: str | None,
        dependency_hierarchy: list[type],
    ) -> set[object] | None:
        target_type = get_args(type_)[0]
        resolved_types = self.__resolve_all_types(target_type)
        if resolved_types is None:
            if is_optional(type_):
                return None
            raise NoSuchPodError(type_)
        return {
            instance
            for _, instance in {
                self.__get_instance_by_type(
                    resolved_type,
                    name,
                    resolved_type,
                    dependency_hierarchy,
                )
                for resolved_type in resolved_types
            }
        }

    def __get_internal_as_dict(
        self,
        type_: GenericAlias,
        name: str | None,
        dependency_hierarchy: list[type],
    ) -> dict[str, object] | None:
        key_type = get_args(type_)[0]
        target_type = get_args(type_)[1]
        if key_type != str:
            return None
        resolved_types = self.__resolve_all_types(target_type)
        if resolved_types is None:
            if is_optional(type_):
                return None
            raise NoSuchPodError(type_)
        return {
            name: instance
            for name, instance in {
                self.__get_instance_by_type(
                    resolved_type,
                    name,
                    resolved_type,
                    dependency_hierarchy,
                )
                for resolved_type in resolved_types
            }
        }

    def __get_internal(
        self,
        type_: type[object],
        name: str | None = None,
        dependency_hierarchy: list[type] | None = None,
    ) -> object | None:
        if isinstance(type_, str):  # To support forward references
            type_ = self.__forward_type_map[type_]  # pragma: no cover
        if dependency_hierarchy is None:
            dependency_hierarchy = []
        if type_ in dependency_hierarchy:
            raise CircularDependencyGraphDetectedError(dependency_hierarchy + [type_])
        resolved_type: type | None = self.__resolve_single_type_or_none(type_, name)
        if resolved_type is not None:
            _, instance = self.__get_instance_by_type(
                type_,
                name,
                resolved_type,
                dependency_hierarchy,
            )
            return instance
        origin_type: GenericAlias | None = get_origin(type_)
        args = get_args(type_)
        if origin_type is not None:
            if origin_type == list:
                return self.__get_internal_as_list(
                    origin_type[args],
                    name,
                    dependency_hierarchy,
                )
            if origin_type == set:
                return self.__get_internal_as_set(
                    origin_type[args],
                    name,
                    dependency_hierarchy,
                )
            if origin_type == dict:
                return self.__get_internal_as_dict(
                    origin_type[args],
                    name,
                    dependency_hierarchy,
                )
        if is_optional(type_):
            return None
        raise NoSuchPodError(type_)

    def __all_internal(
        self,
        type_: type[object],
        dependency_hierarchy: list[type] | None = None,
    ) -> dict[str, object]:
        return {
            pod.name: self.__get_internal(pod.type_, pod.name, dependency_hierarchy)
            for pod in self.__pods
            if pod.type_ == type_
        }

    def get(self, type_: type[ObjectT], name: str | None = None) -> ObjectT:
        return cast(ObjectT, self.__get_internal(type_, name))

    def all(self, type_: type[ObjectT]) -> dict[str, ObjectT]:
        return cast(dict[str, ObjectT], self.__all_internal(type_))

    def contains(self, type_: type, name: str | None = None) -> bool:
        try:
            return self.__resolve_single_type_or_none(type_, name) is not None
        except NoUniquePodError:
            return True

    def find(self, selector: Callable[[Pod], bool]) -> dict[str, object]:
        return {
            pod.name: self.__get_internal(pod.type_, pod.name)
            for pod in self.__pods
            if selector(pod)
        }

    def register(self, obj: PodType) -> None:
        if not Pod.exists(obj):
            raise CannotRegisterNonPodObjectError(obj)
        self.__register_pod_definition(Pod.get(obj))

    def register_post_processor(self, post_processor: IPodPostProcessor) -> None:
        self.__post_processors.append(post_processor)
        self.__post_processors.sort(
            key=lambda x: Order.get_or_default(x, Order(sys.maxsize)).order
        )

    def register_plugin(self, plugin: IPluggable) -> None:
        plugin.register(self)

    def scan(self, package: Module, exclude: set[Module] | None = None) -> None:
        modules: set[ModuleType]
        if exclude is None:
            exclude = set()

        if is_package(package):
            modules = list_modules(package, exclude)
        else:
            modules = {resolve_module(package)}

        for module in modules:
            for obj in list_objects(module, Pod.exists):
                self.register(obj)

    def start(self) -> None:
        for pod in self.__pods:
            if Lazy.exists(pod.target):
                continue
            self.__create_pod_instance(pod, [])
