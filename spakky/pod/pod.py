import inspect
from enum import Enum, auto
from uuid import UUID, uuid4
from typing import TypeVar, Callable, TypeAlias
from inspect import Parameter, isclass, isfunction
from dataclasses import field, dataclass

from spakky.core.annotation import Annotation
from spakky.core.interfaces.equatable import IEquatable
from spakky.core.types import AnyT
from spakky.pod.error import SpakkyPodError
from spakky.utils.casing import pascal_to_snake
from spakky.utils.inspection import has_default_constructor, is_instance_method

DependencyMap: TypeAlias = dict[str, type[object]]
PodType: TypeAlias = Callable[..., object] | type[object]
PodT = TypeVar("PodT", bound=PodType)


class CannotDeterminePodTypeError(SpakkyPodError):
    message = "Cannot determine pod type"


class CannotUseVarArgsInPodError(SpakkyPodError):
    message = "Cannot use var args (*args or **kwargs) in pod"


@dataclass
class Pod(Annotation, IEquatable):
    class Scope(Enum):
        SINGLETON = auto()
        FACTORY = auto()

    id: UUID = field(init=False, default_factory=uuid4)
    name: str = field(kw_only=True, default="")
    scope: Scope = field(kw_only=True, default=Scope.SINGLETON)
    type_: type = field(init=False)
    obj: PodType = field(init=False)
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
            if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                raise CannotUseVarArgsInPodError(obj, parameter.name)
            if parameter.annotation == Parameter.empty:
                raise CannotDeterminePodTypeError(obj, parameter.name)
            dependencies[parameter.name] = parameter.annotation

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
            raise CannotDeterminePodTypeError
        if not self.name:
            self.name = pascal_to_snake(obj.__name__)
        self.type_ = type_
        self.obj = obj
        self.dependencies = dependencies

    def __call__(self, obj: AnyT) -> AnyT:
        self.__initialize(obj)
        return super().__call__(obj)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Pod):
            return False
        return self.id == value.id
