import inspect
from inspect import Parameter, Signature
from dataclasses import field, dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.generics import FuncT
from spakky.dependency.error import SpakkyDependencyError


class Unknown:
    ...


class CannotAutowiringNonConstructorMethodError(SpakkyDependencyError):
    ...


@dataclass
class Autowired(FunctionAnnotation):
    dependencies: dict[str, type] = field(init=False, default_factory=dict[str, type])

    def __call__(self, obj: FuncT) -> FuncT:
        if obj.__name__ != "__init__":
            raise CannotAutowiringNonConstructorMethodError
        signature: Signature = inspect.signature(obj)
        # Ignore self instance pointer argument in dependencies map
        parameters: list[Parameter] = list(signature.parameters.values())[1:]
        for parameter in parameters:
            if parameter.annotation == Parameter.empty:
                # Mark unknown type (no type annotated)
                self.dependencies[parameter.name] = Unknown
                continue
            self.dependencies[parameter.name] = parameter.annotation
        return super().__call__(obj)


def autowired(func: FuncT) -> FuncT:
    return Autowired()(func)
