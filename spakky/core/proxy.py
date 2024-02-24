from abc import abstractmethod
from types import new_class
from typing import (
    Any,
    Generic,
    TypeVar,
    Callable,
    Protocol,
    ParamSpec,
    runtime_checkable,
)
from functools import wraps

from spakky.core.types import ObjectT

P = ParamSpec("P")
R = TypeVar("R")


@runtime_checkable
class IInvocationHandler(Protocol):
    @abstractmethod
    def intercept(
        self,
        target: object,
        method: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        ...


class Enhancer(Generic[ObjectT]):
    __super_class: type[ObjectT]
    __callback: IInvocationHandler

    def __init__(self, super_class: type[ObjectT], callback: IInvocationHandler) -> None:
        self.__super_class = super_class
        self.__callback = callback

    def create(self, *args: Any, **kwargs: Any) -> ObjectT:
        def __getattribute__(instance: ObjectT, name: str) -> Any:
            attr: Any = object.__getattribute__(instance, name)
            if callable(attr):

                @wraps(attr)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    return self.__callback.intercept(instance, attr, *args, **kwargs)

                return wrapper
            return attr

        return new_class(
            name=f"Dynamic{self.__super_class.__name__}ProxyByEnhancer",
            bases=(self.__super_class,),
            exec_body=lambda namespace: namespace.update(
                {"__getattribute__": __getattribute__}
            ),
        )(*args, **kwargs)
