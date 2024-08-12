import inspect
from typing import TypeVar, Callable, TypeAlias
from inspect import Parameter, Signature, isfunction
from dataclasses import field, dataclass

from spakky.core.annotation import Annotation
from spakky.core.types import AnyT
from spakky.injectable.error import SpakkyInjectableError
from spakky.utils.casing import pascal_to_snake
from spakky.utils.inspection import has_default_constructor, is_instance_method

DependencyMap: TypeAlias = dict[str, type[object]]
InjectableType: TypeAlias = Callable[..., object] | type[object]
InjectableT = TypeVar("InjectableT", bound=InjectableType)


class UnknownType: ...


@dataclass
class Injectable(Annotation):
    name: str = field(kw_only=True, default="")
    type_: type[object] = field(init=False)
    dependencies: DependencyMap = field(init=False, default_factory=dict)

    def __get_dependencies(self, obj: InjectableType) -> DependencyMap:
        dependencies: DependencyMap = {}
        if isinstance(obj, type):
            if has_default_constructor(obj):
                return dependencies
            obj = obj.__init__  # Get constructor if obj is a class
        signature: Signature = inspect.signature(obj)
        parameters: list[Parameter] = list(signature.parameters.values())
        if is_instance_method(obj):
            # Remove self parameter if obj is an instance method
            parameters = parameters[1:]

        for parameter in parameters:
            if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                raise CannotUseVarArgsInInjectableError
            if parameter.annotation == Parameter.empty:
                dependencies[parameter.name] = UnknownType
                continue
            dependencies[parameter.name] = parameter.annotation
        return dependencies

    def __initialize(self, obj: InjectableType) -> None:
        injectable_type: type[object] | None = None
        dependencies: DependencyMap = self.__get_dependencies(obj)
        if isinstance(obj, type):
            # If obj is a class, then the injectable type is the class itself
            injectable_type = obj
        if isfunction(obj):
            # If obj is a function,
            # then the injectable type is the return type of the function
            return_type: type = inspect.signature(obj).return_annotation
            if return_type != Parameter.empty:
                injectable_type = return_type
        if injectable_type is None:
            raise CannotDetermineInjectableTypeError()
        if not self.name:
            self.name = pascal_to_snake(obj.__name__)
        self.type_ = injectable_type
        self.dependencies = dependencies

    def __call__(self, obj: AnyT) -> AnyT:
        self.__initialize(obj)
        return super().__call__(obj)


class CannotDetermineInjectableTypeError(SpakkyInjectableError):
    message = "Cannot determine injectable type"


class CannotUseVarArgsInInjectableError(SpakkyInjectableError):
    message = "Cannot use var args (*args or **kwargs) in injectable"
