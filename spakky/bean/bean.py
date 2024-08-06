import inspect
from typing import TypeVar, Callable, TypeAlias
from inspect import Parameter, Signature, isfunction
from dataclasses import field, dataclass

from spakky.bean.error import SpakkyBeanError
from spakky.core.annotation import Annotation
from spakky.core.types import AnyT, Func
from spakky.utils.casing import pascal_to_snake
from spakky.utils.inspection import has_default_constructor, is_instance_method

DependencyMap: TypeAlias = dict[str, type[object]]
BeanFactoryType: TypeAlias = Callable[[], object]
BeanFactoryT = TypeVar("BeanFactoryT", bound=BeanFactoryType)


class UnknownType: ...


class CannotDetermineBeanTypeError(SpakkyBeanError):
    message = "Cannot determine bean type"


@dataclass
class Bean(Annotation):
    bean_name: str = field(kw_only=True, default="")
    bean_type: type[object] = field(init=False)
    dependencies: DependencyMap = field(init=False, default_factory=dict)

    def __get_dependencies(self, obj: type[object] | Func) -> DependencyMap:
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
            if parameter.annotation == Parameter.empty:
                dependencies[parameter.name] = UnknownType
                continue
            dependencies[parameter.name] = parameter.annotation
        return dependencies

    def __initialize(self, obj: type[object] | Func) -> None:
        bean_type: type[object] | None = None
        dependencies: DependencyMap = self.__get_dependencies(obj)
        if isinstance(obj, type):
            # If obj is a class, then the bean type is the class itself
            bean_type = obj
        if isfunction(obj):
            # If obj is a function, then the bean type is the return type of the function
            return_type: type = inspect.signature(obj).return_annotation
            if return_type != Parameter.empty:
                bean_type = return_type
        if bean_type is None:
            raise CannotDetermineBeanTypeError()
        if not self.bean_name:
            self.bean_name = pascal_to_snake(obj.__name__)
        self.bean_type = bean_type
        self.dependencies = dependencies

    def __call__(self, obj: AnyT) -> AnyT:
        self.__initialize(obj)
        return super().__call__(obj)
