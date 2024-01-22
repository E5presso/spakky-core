import inspect
from inspect import Parameter, Signature
from dataclasses import field, dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.generics import FuncT


@dataclass
class Autowired(FunctionAnnotation):
    dependencies: dict[str, type] = field(init=False, default_factory=dict[str, type])

    def __call__(self, obj: FuncT) -> FuncT:
        signature: Signature = inspect.signature(obj)
        self.dependencies = {
            name: parameter.annotation
            for name, parameter in signature.parameters.items()
            if parameter.annotation != Parameter.empty
        }
        return super().__call__(obj)


def autowired(func: FuncT) -> FuncT:
    return Autowired()(func)
