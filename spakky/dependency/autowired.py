import inspect
from inspect import Parameter, Signature
from dataclasses import field, dataclass

from spakky.core.annotation import FunctionAnnotation
from spakky.core.generics import FuncT
from spakky.dependency.error import SpakkyDependencyError


class Unknown:
    """Marker class for unknown type hint"""

    ...


class CannotAutowiringNonConstructorMethodError(SpakkyDependencyError):
    """`Autowired` annotation only can be decorate to `__init__` function.\n
    `Autowired` is only for constructor for class.
    """

    message = "`Autowired` annotation only can be decorate to `__init__` function."


@dataclass
class Autowired(FunctionAnnotation):
    """`Autowired` annotation for constructor of class

    Usage:
        ```python
        class A:
            @Autowired()
            def __init__(self) -> None:
                ...
        ```

    Raises:
        CannotAutowiringNonConstructorMethodError: `Autowired` annotation
        only can be decorate to `__init__` function
    """

    dependencies: dict[str, type[object]] = field(
        init=False, default_factory=dict[str, type[object]]
    )

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
    """`autowired` decorator for constructor of class

    Args:
        func (FuncT): `__init__` function of class

    Returns:
        FuncT: decorated `__init__` function of class
    """
    return Autowired()(func)
