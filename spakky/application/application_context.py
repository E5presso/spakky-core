from abc import ABC
from copy import deepcopy
from typing import Callable, cast, overload

from spakky.application.interfaces.application_context import (
    ApplicationContextAlreadyStartedError,
    ApplicationContextAlreadyStoppedError,
    IApplicationContext,
)
from spakky.core.types import ObjectT
from spakky.pod.interfaces.container import (
    CannotRegisterNonPodObjectError,
    CircularDependencyGraphDetectedError,
    NoSuchPodError,
    NoUniquePodError,
    PodNameAlreadyExistsError,
)
from spakky.pod.interfaces.post_processor import IPostProcessor
from spakky.pod.lazy import Lazy
from spakky.pod.order import Order
from spakky.pod.pod import Pod, PodType
from spakky.pod.post_processors.aware_post_processor import (
    ApplicationContextAwareProcessor,
)
from spakky.pod.qualifier import Qualifier


class ApplicationContext(IApplicationContext, ABC):
    __pods: dict[str, Pod]
    __forward_type_map: dict[str, type]
    __singleton_cache: dict[str, object]
    __post_processors: list[IPostProcessor]
    __is_started: bool

    def __init__(self) -> None:
        self.__forward_type_map = {}
        self.__pods = {}
        self.__singleton_cache = {}
        self.__post_processors = []
        self.__is_started = False

    def __resolve_pod(self, type_: type, qualifier: Qualifier | None) -> Pod | None:
        pods: set[Pod] = {
            pod for pod in self.__pods.values() if pod.is_family_with(type_)
        }
        if len(pods) < 1:
            return None
        if len(pods) > 1:
            candidates: set[Pod] = {
                pod
                for pod in pods
                if (qualifier.selector(pod) if qualifier is not None else pod.is_primary)
            }
            if len(candidates) == 1:
                return candidates.pop()
            raise NoUniquePodError(type_)
        return pods.pop()

    def __instantiate_pod(self, pod: Pod, dependency_hierarchy: list[type]) -> object:
        if pod.type_ in dependency_hierarchy:
            raise CircularDependencyGraphDetectedError(dependency_hierarchy + [pod.type_])
        dependency_hierarchy.append(pod.type_)
        dependencies = {
            name: self.__get_internal(
                type_=dependency.type_,
                name=name,
                dependency_hierarchy=deepcopy(dependency_hierarchy),
                qualifier=dependency.qualifier,
            )
            for name, dependency in pod.dependencies.items()
        }
        instance: object = pod.instantiate(dependencies=dependencies)
        post_processed: object = self.__post_process_pod(instance)
        return post_processed

    def __post_process_pod(self, pod: object) -> object:
        for post_processor in self.__post_processors:
            pod = post_processor.post_process(pod)
        return pod

    def __register_post_processors(self) -> None:
        self._add_post_processor(ApplicationContextAwareProcessor(self))
        post_processors: list[IPostProcessor] = cast(
            list[IPostProcessor],
            list(
                self.find(
                    lambda x: issubclass(
                        x.type_,
                        IPostProcessor,
                    )
                ),
            ),
        )
        post_processors.sort(key=lambda x: Order.get_or_default(x, Order()).order)
        for post_processor in post_processors:
            self._add_post_processor(post_processor)

    def __initialize_pods(self) -> None:
        for pod in self.__pods.values():
            if Lazy.exists(pod.target):
                continue
            if self.__get_internal(type_=pod.type_, name=pod.name) is None:
                raise NoSuchPodError(pod.name, pod.type_)

    def __set_singleton_cache(self, pod: Pod, instance: object) -> None:
        if pod.scope == Pod.Scope.SINGLETON:
            self.__singleton_cache[pod.name] = instance

    def __get_singleton_cache(self, pod: Pod) -> object | None:
        return self.__singleton_cache.get(pod.name)

    def __get_internal(
        self,
        type_: type[ObjectT] | None,
        name: str | None,
        dependency_hierarchy: list[type] | None = None,
        qualifier: Qualifier | None = None,
    ) -> ObjectT | None:
        if dependency_hierarchy is None:
            # If dependency_hierarchy is None
            # it means that this is the first call on recursive cycle
            dependency_hierarchy = []
        if isinstance(type_, str):  # To support forward references
            type_ = self.__forward_type_map[type_]

        pod: Pod | None

        if type_ is not None:
            pod = self.__resolve_pod(type_=type_, qualifier=qualifier)
        elif name is not None:
            pod = self.__pods.get(name)
        else:
            raise ValueError("Either name or type_ must be provided")

        if pod is None:
            return None

        if (cached := self.__get_singleton_cache(pod)) is not None:
            return cast(ObjectT, cached)
        instance: object = self.__instantiate_pod(
            pod,
            dependency_hierarchy,
        )
        self.__set_singleton_cache(pod, instance)
        return cast(ObjectT, instance)

    def _add_post_processor(self, post_processor: IPostProcessor) -> None:
        self.__post_processors.append(post_processor)

    @property
    def pods(self) -> dict[str, Pod]:
        return deepcopy(self.__pods)

    @property
    def is_started(self) -> bool:
        return self.__is_started

    def find(self, selector: Callable[[Pod], bool]) -> set[object]:
        return {
            self.__get_internal(type_=pod.type_, name=pod.name)
            for pod in self.__pods.values()
            if selector(pod)
        }

    def add(self, obj: PodType) -> None:
        if not Pod.exists(obj):
            raise CannotRegisterNonPodObjectError(obj)
        pod: Pod = Pod.get(obj)
        if pod.name in self.__pods:
            raise PodNameAlreadyExistsError(pod.name)
        for base_type in pod.base_types:
            self.__forward_type_map[base_type.__name__] = base_type
        self.__pods[pod.name] = pod

    def add_singleton_instance(self, name: str, obj: object) -> None:
        if name in self.__singleton_cache:
            raise PodNameAlreadyExistsError(name)
        self.__singleton_cache[name] = obj

    def start(self) -> None:
        if self.__is_started:
            raise ApplicationContextAlreadyStartedError()
        self.__register_post_processors()
        self.__initialize_pods()
        self.__is_started = True

    def stop(self) -> None:
        if not self.__is_started:
            raise ApplicationContextAlreadyStoppedError()
        self.__is_started = False

    @overload
    def get(self, *, name: str) -> object: ...

    @overload
    def get(self, *, type_: type[ObjectT]) -> ObjectT: ...

    @overload
    def get(self, *, name: str, type_: type[ObjectT]) -> ObjectT: ...

    def get(
        self,
        name: str | None = None,
        type_: type[ObjectT] | None = None,
    ) -> ObjectT | object:
        instance = self.__get_internal(type_=type_, name=name)
        if instance is None:
            raise NoSuchPodError(name, type_)
        return instance

    @overload
    def contains(self, *, name: str) -> bool: ...

    @overload
    def contains(self, *, type_: type) -> bool: ...

    @overload
    def contains(self, *, name: str, type_: type) -> bool: ...

    def contains(self, name: str | None = None, type_: type | None = None) -> bool:
        if name is not None:
            return name in self.__pods
        if type_ is not None:
            return any(pod for pod in self.__pods.values() if pod.is_family_with(type_))
        raise ValueError("Either name or type_ must be provided")
