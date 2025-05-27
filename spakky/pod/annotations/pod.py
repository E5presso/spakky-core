import inspect
from dataclasses import dataclass, field
from enum import Enum, auto
from inspect import Parameter, isclass, isfunction
from types import NoneType
from typing import Annotated, TypeAlias, TypeGuard, TypeVar, get_origin

from spakky.core.annotation import Annotation
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.metadata import get_metadata
from spakky.core.mro import generic_mro
from spakky.core.types import Class, Func, is_optional
from spakky.pod.annotations.primary import Primary
from spakky.pod.annotations.qualifier import Qualifier
from spakky.pod.error import PodAnnotationFailedError, PodInstantiationFailedError
from spakky.utils.casing import pascal_to_snake
from spakky.utils.inspection import has_default_constructor, is_instance_method


@dataclass
class DependencyInfo:
    name: str
    type_: Class
    has_default: bool = False
    is_optional: bool = False
    qualifiers: list[Qualifier] = field(default_factory=list[Qualifier])


DependencyMap: TypeAlias = dict[str, DependencyInfo]
PodType: TypeAlias = Func | Class
PodT = TypeVar("PodT", bound=PodType)


class CannotDeterminePodTypeError(PodAnnotationFailedError):
    message = "Cannot determine pod type"


class CannotUseVarArgsInPodError(PodAnnotationFailedError):
    message = "Cannot use var args (*args or **kwargs) in pod"


class CannotUsePositionalOnlyArgsInPodError(PodAnnotationFailedError):
    message = "Cannot use positional-only arguments in pod"


class CannotUseOptionalReturnTypeInPodError(PodAnnotationFailedError):
    message = "Cannot use optional return type in pod"


class UnexpectedDependencyNameInjectedError(PodInstantiationFailedError):
    message = "Unexpected dependency name injected"


class UnexpectedDependencyTypeInjectedError(PodInstantiationFailedError):
    message = "Unexpected dependency type injected"


@dataclass(eq=False)
class Pod(Annotation, IEquatable):
    class Scope(Enum):
        SINGLETON = auto()
        PROTOTYPE = auto()

    name: str = field(kw_only=True, default="")
    scope: Scope = field(kw_only=True, default=Scope.SINGLETON)
    type_: type = field(init=False)
    base_types: set[type] = field(init=False, default_factory=set[type])
    target: PodType = field(init=False)
    dependencies: DependencyMap = field(init=False, default_factory=DependencyMap)

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
            if get_origin(parameter.annotation) is Annotated:
                type_, metadata = get_metadata(parameter.annotation)
                qualifiers = [data for data in metadata if isinstance(data, Qualifier)]
                dependencies[parameter.name] = DependencyInfo(
                    name=parameter.name,
                    type_=type_,
                    has_default=parameter.default != Parameter.empty,
                    is_optional=is_optional(parameter.annotation),
                    qualifiers=qualifiers,
                )
            else:
                dependencies[parameter.name] = DependencyInfo(
                    name=parameter.name,
                    type_=parameter.annotation,
                    is_optional=is_optional(parameter.annotation),
                    has_default=parameter.default != Parameter.empty,
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
        if is_optional(type_):
            raise CannotUseOptionalReturnTypeInPodError
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

    @property
    def dependency_qualifiers(self) -> dict[str, list[Qualifier]]:
        return {
            name: dependency.qualifiers
            for name, dependency in self.dependencies.items()
        }

    def is_family_with(self, type_: type) -> bool:
        return type_ == self.type_ or type_ in self.base_types

    def instantiate(self, dependencies: dict[str, object | None]) -> object:
        final_dependencies: dict[str, object] = {}
        for name, dependency in dependencies.items():
            if name not in self.dependencies:
                raise UnexpectedDependencyNameInjectedError(self.type_, name)
            dependency_info: DependencyInfo = self.dependencies[name]
            if dependency is None:
                if dependency_info.has_default:
                    # If dependency is None and has a default value,
                    # do not include it in the final dependencies
                    # so, the default value will be used
                    continue
                if not dependency_info.is_optional:
                    raise UnexpectedDependencyTypeInjectedError(
                        self.type_,
                        {
                            "name": name,
                            "expected": dependency_info.type_,
                            "actual": NoneType,
                        },
                    )
            final_dependencies[name] = dependency
        return self.target(**final_dependencies)


def is_class_pod(pod: PodType) -> TypeGuard[Class]:
    return isclass(pod)


def is_function_pod(pod: PodType) -> TypeGuard[Func]:
    return isfunction(pod)
