from abc import abstractmethod
from types import MethodType, new_class
from typing import Any, Generic, Protocol, runtime_checkable
from functools import wraps

from spakky.core.types import ObjectT


@runtime_checkable
class IMethodInterceptor(Protocol):
    @abstractmethod
    def intercept(self, method: MethodType, *args: Any, **kwargs: Any) -> Any:
        ...


class Enhancer(Generic[ObjectT]):
    __superclass: type[ObjectT]
    __callback: IMethodInterceptor

    def __init__(self, superclass: type[ObjectT], callback: IMethodInterceptor) -> None:
        self.__superclass = superclass
        self.__callback = callback

    def create(self) -> ObjectT:
        def __getattribute__(instance: ObjectT, name: str) -> Any:
            attribute: Any = object.__getattribute__(instance, name)
            if callable(attribute):
                method = attribute

                @wraps(method)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    return self.__callback.intercept(method, *args, **kwargs)

                return wrapper
            return attribute

        return new_class(
            name=f"{self.__superclass.__name__}DynamicProxyByEnhancer",
            bases=(self.__superclass,),
            exec_body=lambda x: x.update(__getattribute__=__getattribute__),
        )()