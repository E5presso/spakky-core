import sys
from copy import deepcopy
from uuid import UUID
from types import ModuleType
from typing import Callable, cast

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
from spakky.core.types import ObjectT
from spakky.pod.lazy import Lazy
from spakky.pod.order import Order
from spakky.pod.pod import Pod, PodType
from spakky.pod.primary import Primary


class CircularDependencyGraphDetectedError(SpakkyApplicationError):
    message = "Circular dependency detected"


class ApplicationContext(IPodContainer, IPodRegistry, IPluginRegistry):
    __type_name_map: dict[str, type]
    __type_lookup: dict[type, set[type]]  # dict[base: {derived}]
    __pod_lookup: dict[type, UUID]
    __pods: dict[UUID, Pod]
    __singleton_cache: dict[UUID, object]
    __post_processors: list[IPodPostProcessor]

    @property
    def pods(self) -> set[PodType]:
        return {x.obj for x in self.__pods.values()}

    @property
    def post_processors(self) -> set[type[IPodPostProcessor]]:
        return {type(x) for x in self.__post_processors}

    def __init__(
        self,
        package: Module | set[Module] | None = None,
        exclude: set[Module] | None = None,
    ) -> None:
        self.__type_name_map = {}
        self.__type_lookup = {}
        self.__pod_lookup = {}
        self.__pods = {}
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
        for base_type in pod.type_.mro():
            if base_type not in self.__type_lookup:
                self.__type_lookup[base_type] = set()
            self.__type_lookup[base_type].add(pod.type_)
        self.__type_name_map[pod.type_.__name__] = pod.type_
        self.__pod_lookup[pod.type_] = pod.id
        self.__pods[pod.id] = pod

    def __resolve_type(self, type_: type, name: str | None) -> type:
        if type_ not in self.__type_lookup:
            raise NoSuchPodError(type_)
        derived: set[type] = self.__type_lookup[type_]
        if len(derived) > 1:
            derived: set[type] = {
                x for x in derived if Primary.exists(x) or Pod.get(x).name == name
            }
        if len(derived) != 1:
            raise NoUniquePodError(type_, derived)
        return list(derived)[0]

    def __post_process_pod(self, pod: object) -> object:
        for post_processor in self.__post_processors:
            pod = post_processor.post_process(self, pod)
        return pod

    def __create_pod_instance(self, pod: Pod, dependency_hierarchy: list[type]) -> object:
        if pod.scope == Pod.Scope.SINGLETON and pod.id in self.__singleton_cache:
            return self.__singleton_cache[pod.id]
        dependencies: dict[str, object] = {
            name: self.__get_internal(
                type_,
                name,
                deepcopy(dependency_hierarchy),  # Copy to avoid mutation
            )
            for name, type_ in pod.dependencies.items()
        }
        instance: object = pod.obj(**dependencies)
        processed: object = self.__post_process_pod(instance)
        if pod.scope == Pod.Scope.SINGLETON:
            self.__singleton_cache[pod.id] = processed
        return processed

    def __get_internal(
        self,
        type_: type,
        name: str | None = None,
        dependency_hierarchy: list[type] | None = None,
    ) -> object:
        if isinstance(type_, str):  # To support forward references
            type_ = self.__type_name_map[type_]  # pragma: no cover
        if dependency_hierarchy is None:
            dependency_hierarchy = []
        if type_ in dependency_hierarchy:
            raise CircularDependencyGraphDetectedError(dependency_hierarchy + [type_])
        dependency_hierarchy.append(type_)
        resolved_type: type = self.__resolve_type(type_, name)
        pod_id: UUID = self.__pod_lookup[resolved_type]
        pod: Pod = self.__pods[pod_id]
        return self.__create_pod_instance(pod, dependency_hierarchy)

    def get(self, type_: type[ObjectT], name: str | None = None) -> ObjectT:
        return cast(ObjectT, self.__get_internal(type_, name))

    def contains(self, type_: type, name: str | None = None) -> bool:
        try:
            self.__resolve_type(type_, name)
            return True
        except NoUniquePodError:
            return True
        except NoSuchPodError:
            return False

    def find(self, selector: Callable[[Pod], bool]) -> dict[str, object]:
        return {
            pod.name: self.__get_internal(pod.type_, pod.name)
            for pod in self.__pods.values()
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
        for pod in self.__pods.values():
            if Lazy.exists(pod.obj):
                continue
            self.__create_pod_instance(pod, [])
