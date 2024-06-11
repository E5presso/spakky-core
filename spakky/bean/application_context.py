from enum import Enum, auto
from uuid import UUID, uuid4
from types import ModuleType
from typing import Any, Callable, Sequence, overload

from spakky.bean.autowired import Unknown
from spakky.bean.bean import Bean, BeanFactory, BeanFactoryType
from spakky.bean.interfaces.bean_container import (
    IBeanContainer,
    NoSuchBeanError,
    NoUniqueBeanError,
)
from spakky.bean.interfaces.bean_processor import IBeanPostProcessor
from spakky.bean.interfaces.bean_processor_registry import IBeanPostProcessorRegistry
from spakky.bean.interfaces.bean_registry import (
    CannotRegisterNonBeanError,
    CannotRegisterNonBeanFactoryError,
    IBeanRegistry,
)
from spakky.bean.interfaces.bean_scanner import IBeanScanner
from spakky.bean.primary import Primary
from spakky.core.importing import list_classes, list_functions, list_modules
from spakky.core.types import AnyT


class BeanType(Enum):
    CLASS = auto()
    FACTORY = auto()


class ApplicationContext(
    IBeanContainer,
    IBeanRegistry,
    IBeanPostProcessorRegistry,
    IBeanScanner,
):
    __type_map: dict[type, set[type]]
    __bean_map: dict[UUID, type | BeanFactoryType]
    __bean_type_map: dict[type, UUID]
    __bean_name_map: dict[str, UUID]
    __singleton_cache: dict[UUID, object]
    __post_processors: list[IBeanPostProcessor]

    def __init__(self, package: ModuleType | str | None = None) -> None:
        self.__bean_map = {}
        self.__type_map = {}
        self.__bean_type_map = {}
        self.__bean_name_map = {}
        self.__singleton_cache = {}
        self.__post_processors = []
        if package is not None:
            self.scan(package)

    def __set_target_type(self, target_type: type) -> None:
        for base in target_type.__mro__:
            if base not in self.__type_map:
                self.__type_map[base] = set()
            self.__type_map[base].add(target_type)

    def __set_bean(self, bean: type) -> UUID:
        annotation: Bean = Bean.single(bean)
        bean_id: UUID = uuid4()
        self.__bean_type_map[bean] = bean_id
        self.__bean_name_map[annotation.bean_name] = bean_id
        self.__bean_map[bean_id] = bean
        return bean_id

    def __set_bean_factory(self, factory: BeanFactoryType) -> UUID:
        annotation: BeanFactory = BeanFactory.single(factory)
        bean_id: UUID = uuid4()
        self.__bean_type_map[annotation.bean_type] = bean_id
        self.__bean_name_map[annotation.bean_name] = bean_id
        self.__bean_map[bean_id] = factory
        return bean_id

    def __get_target_type(self, required_type: type) -> type:
        if required_type not in self.__type_map:
            raise NoSuchBeanError(required_type)
        derived: set[type] = self.__type_map[required_type]
        if len(derived) > 1:
            marked_as_primary: set[type] = {x for x in derived if Primary.contains(x)}
            if len(marked_as_primary) != 1:
                raise NoUniqueBeanError(required_type, derived, marked_as_primary)
            derived = marked_as_primary
        return list(derived)[0]

    def __get_bean_id_by_type(self, bean_type: type) -> UUID:
        return self.__bean_type_map[bean_type]

    def __get_bean_id_by_name(self, bean_name: str) -> UUID:
        if bean_name not in self.__bean_name_map:
            raise NoSuchBeanError(bean_name)
        return self.__bean_name_map[bean_name]

    def __get_dependencies(self, bean_type: type) -> dict[str, object]:
        annotation: Bean = Bean.single(bean_type)
        dependencies: dict[str, object] = {}
        for name, required_type in annotation.dependencies.items():
            if required_type == Unknown:
                dependencies[name] = self.__retrieve_bean_by_name(name)
                continue
            dependencies[name] = self.__retrieve_bean_by_type(required_type)
        return dependencies

    def __instaniate_bean(self, bean_id: UUID) -> tuple[object, BeanType]:
        bean = self.__bean_map[bean_id]
        if isinstance(bean, type):
            return bean(**self.__get_dependencies(bean)), BeanType.CLASS
        return bean(), BeanType.FACTORY

    def __post_process_bean(self, bean: object) -> object:
        for post_processor in self.__post_processors:
            bean = post_processor.post_process_bean(self, bean)
        return bean

    def __get_bean_by_id(self, bean_id: UUID) -> object:
        if bean_id not in self.__singleton_cache:
            bean, bean_type = self.__instaniate_bean(bean_id)
            if bean_type == BeanType.CLASS:
                bean = self.__post_process_bean(bean)
            self.__singleton_cache[bean_id] = bean
        return self.__singleton_cache[bean_id]

    def __retrieve_bean_by_type(self, bean_type: type) -> object:
        actual_type = self.__get_target_type(bean_type)
        bean_id = self.__get_bean_id_by_type(actual_type)
        return self.__get_bean_by_id(bean_id)

    def __retrieve_bean_by_name(self, name: str) -> Any:
        bean_id = self.__get_bean_id_by_name(name)
        return self.__get_bean_by_id(bean_id)

    @overload
    def contains(self, *, required_type: type) -> bool: ...

    @overload
    def contains(self, *, name: str) -> bool: ...

    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool:
        if required_type is not None:
            if required_type not in self.__type_map:
                return False
            bean_type = self.__get_target_type(required_type)
            return bean_type in self.__bean_type_map
        if name is None:  # pragma: no cover
            raise ValueError("'name' and 'required_type' both cannot be None")
        return name in self.__bean_name_map

    @overload
    def single(self, *, required_type: type[AnyT]) -> AnyT: ...

    @overload
    def single(self, *, name: str) -> Any: ...

    def single(
        self, required_type: type[AnyT] | None = None, name: str | None = None
    ) -> AnyT | Any:
        if required_type is not None:
            return self.__retrieve_bean_by_type(required_type)
        if name is None:  # pragma: no cover
            raise ValueError("'name' and 'required_type' both cannot be None")
        return self.__retrieve_bean_by_name(name)

    def filter_bean_types(self, clause: Callable[[type], bool]) -> Sequence[type]:
        return [x for x in self.__bean_type_map if clause(x)]

    def filter_beans(self, clause: Callable[[type], bool]) -> Sequence[object]:
        filtered: list[type[object]] = [x for x in self.__bean_type_map if clause(x)]
        return [self.single(required_type=x) for x in filtered]

    def register_bean(self, bean: type) -> None:
        if not Bean.contains(bean):
            raise CannotRegisterNonBeanError(bean)
        self.__set_target_type(bean)
        self.__set_bean(bean)

    def register_bean_factory(self, factory: BeanFactoryType) -> None:
        if not BeanFactory.contains(factory):
            raise CannotRegisterNonBeanFactoryError(factory)
        annotation: BeanFactory = BeanFactory.single(factory)
        self.__set_target_type(annotation.bean_type)
        self.__set_bean_factory(factory)

    def register_bean_post_processor(self, post_processor: IBeanPostProcessor) -> None:
        self.__post_processors.append(post_processor)

    def scan(self, package: ModuleType | str) -> None:
        modules: set[ModuleType] = list_modules(package)
        for module in modules:
            beans: set[type] = list_classes(module, Bean.contains)
            factories: set[BeanFactoryType] = list_functions(module, BeanFactory.contains)
            for bean in beans:
                self.register_bean(bean)
            for factory in factories:
                self.register_bean_factory(factory)

    def start(self) -> None:
        for bean_id in self.__bean_map:
            self.__get_bean_by_id(bean_id)
