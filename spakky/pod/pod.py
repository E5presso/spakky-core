import inspect
from enum import Enum, auto
from typing import TypeVar, TypeAlias, TypeGuard
from inspect import Parameter, isclass, isfunction
from dataclasses import field, dataclass

from spakky.core.annotation import Annotation
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.mro import generic_mro
from spakky.core.types import Class, Func, is_optional
from spakky.pod.error import SpakkyPodError
from spakky.pod.primary import Primary
from spakky.utils.casing import pascal_to_snake
from spakky.utils.inspection import has_default_constructor, is_instance_method


@dataclass
class Dependency:
    type_: Class
    has_default: bool
    is_optional: bool


DependencyMap: TypeAlias = dict[str, Dependency]
PodType: TypeAlias = Func | Class
PodT = TypeVar("PodT", bound=PodType)


class CannotDeterminePodTypeError(SpakkyPodError):
    message = "Cannot determine pod type"


class CannotUseVarArgsInPodError(SpakkyPodError):
    message = "Cannot use var args (*args or **kwargs) in pod"


class CannotUsePositionalOnlyArgsInPodError(SpakkyPodError):
    message = "Cannot use positional-only arguments in pod"


@dataclass(eq=False)
class Pod(Annotation, IEquatable):
    class Scope(Enum):
        SINGLETON = auto()
        PROTOTYPE = auto()

    name: str = field(kw_only=True, default="")
    scope: Scope = field(kw_only=True, default=Scope.SINGLETON)
    type_: type = field(init=False)
    base_types: set[type] = field(init=False, default_factory=set)
    target: PodType = field(init=False)
    dependencies: DependencyMap = field(init=False, default_factory=dict)

    def __get_dependencies(self, obj: PodType) -> DependencyMap:
        if isclass(obj):
            if has_default_constructor(obj):
                # If obj is a class with a default constructor,
                # then return an empty dictionary
                return {}
            obj = obj.__init__  # Get constructor if obj is a class
        parameters: list[Parameter] = list(inspect.signature(obj).parameters.values())
        if is_instance_method(obj):
            # Remove self parameter if obj is an instance method
            parameters = parameters[1:]

        dependencies: DependencyMap = {}
        for parameter in parameters:
            if parameter.kind == Parameter.POSITIONAL_ONLY:
                raise CannotUsePositionalOnlyArgsInPodError(obj, parameter.name)
            if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                raise CannotUseVarArgsInPodError(obj, parameter.name)
            if parameter.annotation == Parameter.empty:
                raise CannotDeterminePodTypeError(obj, parameter.name)
            dependencies[parameter.name] = Dependency(
                type_=parameter.annotation,
                has_default=parameter.default != Parameter.empty,
                is_optional=is_optional(parameter.annotation),
            )

        return dependencies

    def __initialize(self, obj: PodType) -> None:
        type_: type | None = None
        dependencies: DependencyMap = self.__get_dependencies(obj)
        if isfunction(obj):
            # If obj is a function,
            # then the pod type is the return type of the function
            return_type: type = inspect.signature(obj).return_annotation
            if return_type == Parameter.empty:
                raise CannotDeterminePodTypeError(obj, return_type)
            type_ = return_type
        if isclass(obj):
            # If obj is a class, then the pod type is the class itself
            type_ = obj
        if type_ is None:
            raise CannotDeterminePodTypeError  # pragma: no cover
        if not self.name:
            self.name = pascal_to_snake(obj.__name__)
        self.type_ = type_
        self.base_types = set(generic_mro(type_))
        self.target = obj
        self.dependencies = dependencies

    def __call__(self, obj: PodT) -> PodT:
        self.__initialize(obj)
        return super().__call__(obj)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, value: object) -> bool:
        if self is value:
            return True
        if not isinstance(value, Pod):
            return False
        return self.name == value.name

    @property
    def is_primary(self) -> bool:
        return Primary.exists(self.target)

    def is_family_with(self, type_: type) -> bool:
        return type_ == self.type_ or type_ in self.base_types

    def instantiate(self, dependencies: dict[str, object | None]) -> object:
        dependencies_without_default_value = {
            name: dependency
            for name, dependency in dependencies.items()
            if not (dependency is None and self.dependencies[name].has_default)
        }
        return self.target(**dependencies_without_default_value)


def is_class_pod(pod: PodType) -> TypeGuard[Class]:
    return isclass(pod)


def is_function_pod(pod: PodType) -> TypeGuard[Func]:
    return isfunction(pod)
