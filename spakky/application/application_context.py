import threading
from asyncio import locks
from asyncio.events import AbstractEventLoop, new_event_loop, set_event_loop
from asyncio.tasks import run_coroutine_threadsafe
from copy import deepcopy
from logging import Logger, getLogger
from threading import Thread
from typing import Callable, cast, overload

from spakky.aop.post_processor import AspectPostProcessor
from spakky.core.mro import is_family_with
from spakky.core.types import ObjectT, is_optional, remove_none
from spakky.pod.annotations.lazy import Lazy
from spakky.pod.annotations.order import Order
from spakky.pod.annotations.pod import Pod, PodType
from spakky.pod.annotations.qualifier import Qualifier
from spakky.pod.interfaces.application_context import (
    ApplicationContextAlreadyStartedError,
    ApplicationContextAlreadyStoppedError,
    EventLoopThreadAlreadyStartedInApplicationContextError,
    EventLoopThreadNotStartedInApplicationContextError,
    IApplicationContext,
)
from spakky.pod.interfaces.container import (
    CannotRegisterNonPodObjectError,
    CircularDependencyGraphDetectedError,
    NoSuchPodError,
    NoUniquePodError,
    PodNameAlreadyExistsError,
)
from spakky.pod.interfaces.post_processor import IPostProcessor
from spakky.pod.post_processors.aware_post_processor import (
    ApplicationContextAwareProcessor,
)
from spakky.service.interfaces.service import IAsyncService, IService
from spakky.service.post_processor import ServicePostProcessor


class ApplicationContext(IApplicationContext):
    __logger: Logger
    __pods: dict[str, Pod]
    __forward_type_map: dict[str, type]
    __singleton_cache: dict[str, object]
    __post_processors: list[IPostProcessor]
    __services: list[IService]
    __async_services: list[IAsyncService]
    __event_loop: AbstractEventLoop | None
    __event_thread: Thread | None
    __is_started: bool

    def __init__(self, logger: Logger | None = None) -> None:
        self.__logger = logger or getLogger()
        self.__forward_type_map = {}
        self.__pods = {}
        self.__singleton_cache = {}
        self.__post_processors = []
        self.__services = []
        self.__async_services = []
        self.__event_loop = None
        self.__event_thread = None
        self.__is_started = False
        self.task_stop_event = locks.Event()
        self.thread_stop_event = threading.Event()

    def __resolve_candidate(
        self,
        type_: type,
        name: str | None,
        qualifiers: list[Qualifier],
    ) -> Pod | None:
        def qualify_pod(pod: Pod) -> bool:
            if any(qualifiers):
                return all(qualifier.selector(pod) for qualifier in qualifiers)
            if name is not None:
                return pod.name == name
            return pod.is_primary

        pods = {pod for pod in self.__pods.values() if pod.is_family_with(type_)}
        if len(pods) < 1:
            return None
        if len(pods) > 1:
            pods = {pod for pod in pods if qualify_pod(pod)}
            if len(pods) == 1:
                return pods.pop()
            raise NoUniquePodError(type_)
        return pods.pop()

    def __instantiate_pod(self, pod: Pod, dependency_hierarchy: list[type]) -> object:
        if pod.type_ in dependency_hierarchy:
            raise CircularDependencyGraphDetectedError(
                dependency_hierarchy + [pod.type_]
            )
        dependency_hierarchy.append(pod.type_)
        dependencies = {
            name: self.__get_internal(
                type_=remove_none(dependency.type_)
                if is_optional(dependency.type_)
                else dependency.type_,
                name=name,
                dependency_hierarchy=deepcopy(dependency_hierarchy),
                qualifiers=dependency.qualifiers,
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
        self.__add_post_processor(ApplicationContextAwareProcessor(self, self.__logger))
        self.__add_post_processor(AspectPostProcessor(self, self.__logger))
        self.__add_post_processor(ServicePostProcessor(self, self.__logger))

        post_processors: list[IPostProcessor] = cast(
            list[IPostProcessor],
            list(
                self.find(lambda x: IPostProcessor in x.base_types),
            ),
        )
        post_processors.sort(key=lambda x: Order.get_or_default(x, Order()).order)
        for post_processor in post_processors:
            self.__add_post_processor(post_processor)

    def __initialize_pods(self) -> None:
        for pod in self.__pods.values():
            if Lazy.exists(pod.target):
                continue
            if self.__get_internal(type_=pod.type_, name=pod.name) is None:
                raise NoSuchPodError(pod.name, pod.type_)

    def __clear_all(self) -> None:
        self.__pods.clear()
        self.__forward_type_map.clear()
        self.__singleton_cache.clear()
        self.__post_processors.clear()
        self.__services.clear()
        self.__async_services.clear()

    def __set_singleton_cache(self, pod: Pod, instance: object) -> None:
        if pod.scope == Pod.Scope.SINGLETON:
            self.__singleton_cache[pod.name] = instance

    def __get_singleton_cache(self, pod: Pod) -> object | None:
        return self.__singleton_cache.get(pod.name)

    def __get_internal(
        self,
        type_: type[ObjectT],
        name: str | None,
        dependency_hierarchy: list[type] | None = None,
        qualifiers: list[Qualifier] | None = None,
    ) -> ObjectT | None:
        if dependency_hierarchy is None:
            # If dependency_hierarchy is None
            # it means that this is the first call on recursive cycle
            dependency_hierarchy = []
        if qualifiers is None:
            # If qualifiers is None, it means that no qualifier is specified
            qualifiers = []
        if isinstance(type_, str):  # To support forward references
            if type_ not in self.__forward_type_map:
                return None
            type_ = self.__forward_type_map[type_]

        if is_family_with(type_, Logger):
            return cast(ObjectT, self.__logger)
        pod = self.__resolve_candidate(type_=type_, name=name, qualifiers=qualifiers)
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

    def __add_post_processor(self, post_processor: IPostProcessor) -> None:
        self.__post_processors.append(post_processor)

    def __run_event_loop(self, loop: AbstractEventLoop) -> None:
        set_event_loop(loop)
        loop.run_forever()
        loop.close()

    def __start_services(self) -> None:
        if self.__event_loop is not None:
            raise EventLoopThreadAlreadyStartedInApplicationContextError
        if self.__event_thread is not None:
            raise EventLoopThreadAlreadyStartedInApplicationContextError

        self.__event_loop = new_event_loop()
        self.__event_thread = Thread(
            target=self.__run_event_loop,
            args=(self.__event_loop,),
            daemon=True,
        )
        self.__event_thread.start()

        for service in self.__services:
            service.start()

        async def start_async_services() -> None:
            if self.__event_loop is None:
                raise EventLoopThreadNotStartedInApplicationContextError
            for service in self.__async_services:
                await service.start_async()

        run_coroutine_threadsafe(start_async_services(), self.__event_loop).result()

    def __stop_services(self) -> None:
        if self.__event_loop is None:
            raise EventLoopThreadNotStartedInApplicationContextError
        if self.__event_thread is None:
            raise EventLoopThreadNotStartedInApplicationContextError

        for service in self.__services:
            service.stop()

        async def stop_async_services() -> None:
            if self.__event_loop is None:
                raise EventLoopThreadNotStartedInApplicationContextError
            for service in self.__async_services:
                await service.stop_async()

        run_coroutine_threadsafe(stop_async_services(), self.__event_loop).result()
        self.__event_loop.call_soon_threadsafe(self.__event_loop.stop)
        self.__event_thread.join()
        self.__event_loop = None
        self.__event_thread = None

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

    def add_service(self, service: IService | IAsyncService) -> None:
        if isinstance(service, IService):
            self.__services.append(service)
        if isinstance(service, IAsyncService):
            self.__async_services.append(service)

    def start(self) -> None:
        if self.__is_started:
            raise ApplicationContextAlreadyStartedError()
        self.__is_started = True
        self.__register_post_processors()
        self.__initialize_pods()
        self.__start_services()

    def stop(self) -> None:
        if not self.__is_started:
            raise ApplicationContextAlreadyStoppedError()
        self.__stop_services()
        self.__clear_all()
        self.__is_started = False

    @overload
    def get(self, type_: type[ObjectT]) -> ObjectT: ...

    @overload
    def get(self, type_: type[ObjectT], name: str) -> ObjectT: ...

    def get(
        self,
        type_: type[ObjectT],
        name: str | None = None,
    ) -> ObjectT | object:
        instance = self.__get_internal(type_=type_, name=name)
        if instance is None:
            raise NoSuchPodError(name, type_)
        return instance

    @overload
    def contains(self, type_: type) -> bool: ...

    @overload
    def contains(self, type_: type, name: str) -> bool: ...

    def contains(self, type_: type, name: str | None = None) -> bool:
        if name is not None:
            return name in self.__pods
        return any(pod for pod in self.__pods.values() if pod.is_family_with(type_))
