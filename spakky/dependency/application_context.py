from types import ModuleType
from typing import Any, Callable, Sequence, overload

from spakky.core.generics import ObjectT
from spakky.core.importing import list_classes, list_modules
from spakky.dependency.autowired import Unknown
from spakky.dependency.component import Component
from spakky.dependency.error import SpakkyDependencyError
from spakky.dependency.interfaces.dependency_container import IDependencyContainer
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)
from spakky.dependency.interfaces.managed_dependency_scanner import (
    IManagedDependencyScanner,
)
from spakky.dependency.interfaces.managed_registry import IManagedDependencyRegistry
from spakky.dependency.interfaces.unmanaged_dependency_registry import (
    IUnmanagedDependencyRegistry,
)
from spakky.dependency.plugin import PostProcessor
from spakky.dependency.primary import Primary
from spakky.dependency.provider import Provider, ProvidingType


class CannotRegisterNonComponentError(SpakkyDependencyError):
    """Cannot register non-component class.\n
    The component class must be decorated by `@Component()`
    """

    message = "Cannot register non-component class."


class NoSuchComponentError(SpakkyDependencyError):
    """Cannot find component from context by given condition"""

    message = "Cannot find component from context by given condition"


class NoUniqueComponentError(SpakkyDependencyError):
    """Multiple component found by given condition\n
    You can mark component as `@Primary()` to uniquify component
    """

    message = "Multiple component found by given condition"


class ApplicationContext(
    IDependencyContainer,
    IManagedDependencyRegistry,
    IUnmanagedDependencyRegistry,
    IManagedDependencyScanner,
):
    """Component context manager for DI/IoC\n
    You can manually register component or auto-scanning\n
    components that decorated by `@Component` or children from it\n
    The component provided by singleton or factory.

    Raises:
        CannotRegisterNonComponentError: Cannot register non-component class
        NoSuchComponentError: Cannot find component by given condition
        NoUniqueComponentError: Multiple component found by given condition
    """

    __components: list[type]
    __type_map: dict[type, set[type]]
    __components_type_map: dict[type, type]
    __components_name_map: dict[str, type]
    __singleton_cache: dict[type, object]
    __unmanaged_dependencies: dict[str, Any]

    def __init__(self, package: ModuleType | None = None) -> None:
        """Initialize context

        Args:
            package (ModuleType | None, optional): package to start full-scan.
            Defaults to None.
        """
        self.__components = []
        self.__type_map = {}
        self.__components_type_map = {}
        self.__components_name_map = {}
        self.__singleton_cache = {}
        self.__unmanaged_dependencies = {}
        if package is not None:
            self.scan(package)

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

    def __apply_post_processor(self, instance: Any) -> Any:
        if PostProcessor.contains(instance):
            return instance
        post_processors = self.where(PostProcessor.contains)
        for post_processor in post_processors:
            if isinstance(post_processor, IDependencyPostProcessor):
                instance = post_processor.process_dependency(self, instance)
        return instance

    def __initialize_dependency(
        self, component: type, dependencies: dict[str, object]
    ) -> Any:
        instance = component(**dependencies)
        instance = self.__apply_post_processor(instance)
        return instance

    def __get_instance(self, component: type, providing_type: ProvidingType) -> object:
        component_annotation: Component = Component.single(component)
        dependencies: dict[str, object] = {}
        for name, required_type in component_annotation.dependencies.items():
            if required_type == Unknown:
                dependencies[name] = self.get(name=name)
                continue
            try:
                dependencies[name] = self.get(required_type=required_type)
            except NoSuchComponentError:
                dependencies[name] = self.get(name=name)
        if providing_type == ProvidingType.FACTORY:
            return self.__initialize_dependency(component, dependencies)
        if component not in self.__singleton_cache:
            self.__singleton_cache[component] = self.__initialize_dependency(
                component,
                dependencies,
            )
            return self.__singleton_cache[component]
        return self.__singleton_cache[component]

    def register_component(self, component: type) -> None:
        """Manually register component to context

        Args:
            component (type): Component class to register

        Raises:
            CannotRegisterNonComponentError: Cannot register non-component class
        """
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

    def register_unmanaged_dependency(self, name: str, dependency: Any) -> None:
        self.__unmanaged_dependencies[name] = dependency

    def scan(self, package: ModuleType) -> None:
        """Auto-scan from given package-module

        Args:
            package (ModuleType): package-module to start full-scan components
        """
        modules: set[ModuleType] = list_modules(package)
        for module in modules:
            components: set[type] = list_classes(module, Component.contains)
            for component in components:
                self.register_component(component)

    def initialize(self) -> None:
        for component in self.__components:
            self.__get_instance(
                component,
                Provider.single(component).providing_type
                if Provider.contains(component)
                else ProvidingType.SINGLETON,
            )

    def clear_singleton_cache(self) -> None:
        self.__singleton_cache = {}

    @overload
    def contains(self, *, required_type: type) -> bool:
        """Check existance of component by given condition

        Args:
            required_type (type | None, optional): Required type to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        ...

    @overload
    def contains(self, *, name: str) -> bool:
        """Check existance of component by given condition

        Args:
            name (str | None, optional): Name to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        ...

    def contains(
        self, required_type: type | None = None, name: str | None = None
    ) -> bool:
        """Check existance of component by given condition

        Args:
            required_type (type | None, optional): Required type to check existance.
            Defaults to None.
            name (str | None, optional): Name to check existance.
            Defaults to None.

        Returns:
            bool: True if component found in context
        """
        if required_type is not None:
            return required_type in self.__components_type_map
        if name in self.__components_name_map:
            return True
        return name in self.__unmanaged_dependencies

    @overload
    def get(self, *, required_type: type[ObjectT]) -> ObjectT:
        """Retrieve component by given condition

        Args:
            required_type (type[ObjectT] | None, optional): Required type to
            get component. Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            ObjectT: Retrieved component by given condition
        """
        ...

    @overload
    def get(self, *, name: str) -> Any:
        """Retrieve component by given condition

        Args:
            name (str | None, optional): Name to get component.
            Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            object: Retrieved component by given condition
        """

    def get(
        self, required_type: type[ObjectT] | None = None, name: str | None = None
    ) -> ObjectT | Any:
        """Retrieve component by given condition

        Args:
            required_type (type[ObjectT] | None, optional): Required type to
            get component. Defaults to None.
            name (str | None, optional): Name to get component.
            Defaults to None.

        Raises:
            NoSuchComponentError: Cannot find component from context by given condition

        Returns:
            ObjectT | object: Retrieved component by given condition
        """
        if name is not None:
            if name not in self.__components_name_map:
                if name not in self.__unmanaged_dependencies:
                    raise NoSuchComponentError(name)
                return self.__unmanaged_dependencies[name]
            component: type = self.__components_name_map[name]
            provider_annotation: Provider | None = Provider.single_or_none(component)
            providing_type: ProvidingType = (
                provider_annotation.providing_type
                if provider_annotation is not None
                else ProvidingType.SINGLETON
            )
            return self.__get_instance(component=component, providing_type=providing_type)
        if required_type is None:  # pragma: no cover
            raise ValueError("'name' and 'required_type' both cannot be None")
        target: type = self.__get_target_type(required_type)
        component: type = self.__components_type_map[target]
        provider_annotation: Provider | None = Provider.single_or_none(component)
        providing_type: ProvidingType = (
            provider_annotation.providing_type
            if provider_annotation is not None
            else ProvidingType.SINGLETON
        )
        return self.__get_instance(component=component, providing_type=providing_type)

    def where(self, clause: Callable[[type], bool]) -> Sequence[object]:
        """Query components from context by given clause

        Args:
            clause (Callable[[type], bool]): Given clause to query components

        Returns:
            Sequence[object]: Queried components by given clause
        """
        return [
            self.__get_instance(
                component,
                Provider.single(component).providing_type
                if Provider.contains(component)
                else ProvidingType.SINGLETON,
            )
            for component in self.__components
            if clause(component)
        ]
