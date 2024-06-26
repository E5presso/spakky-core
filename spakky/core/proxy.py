from abc import ABC, abstractmethod
from types import new_class
from typing import Any, Generic, ClassVar, Iterable, Protocol, runtime_checkable
from functools import wraps

from spakky.core.types import AsyncFunc, Func, ObjectT, is_async_function, is_function


@runtime_checkable
class _IProxyHandler(Protocol):
    @abstractmethod
    def call(self, method: Func, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    def get(self, name: str, value: Any) -> Any: ...

    @abstractmethod
    def set(self, name: str, value: Any) -> Any: ...

    @abstractmethod
    def delete(self, name: str, value: Any) -> Any: ...


class AbstractProxyHandler(ABC, _IProxyHandler):
    def call(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        return method(*args, **kwargs)

    async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        return await method(*args, **kwargs)

    def get(self, name: str, value: Any) -> Any:
        return value

    def set(self, name: str, value: Any) -> Any:
        return value

    def delete(self, name: str, value: Any) -> Any:
        return value


class ProxyFactory(Generic[ObjectT]):
    __PROXY_CLASS_NAME_SUFFIX: ClassVar[str] = "ProxyByFactory"
    __ATTRIBUTES_TO_IGNORE: ClassVar[Iterable[str]] = [
        "__dict__",
        "__class__",
        "__weakref__",
        "__base__",
        "__bases__",
        "__mro__",
        "__subclasses__",
        "__name__",
        "__qualname__",
        "__module__",
        "__annotations__",
        "__doc__",
    ]

    __superclass: type[ObjectT]
    __handler: _IProxyHandler

    def __init__(self, superclass: type[ObjectT], handler: _IProxyHandler) -> None:
        self.__superclass = superclass
        self.__handler = handler

    def create(self, *args: Any, **kwargs: Any) -> ObjectT:
        def __getattribute__(instance: ObjectT, name: str) -> Any:
            value: Any = object.__getattribute__(instance, name)
            if is_function(value):

                @wraps(value)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    return __call__(value, *args, **kwargs)

                return wrapper

            if name in self.__ATTRIBUTES_TO_IGNORE:
                return value
            return __getattr__(name, value)

        def __call__(method: Func | AsyncFunc, *args: Any, **kwargs: Any) -> Any:
            if is_async_function(method):
                return self.__handler.call_async(method, *args, **kwargs)
            return self.__handler.call(method, *args, **kwargs)

        def __getattr__(name: str, value: Any) -> Any:
            return self.__handler.get(name, value)

        def __setattr__(instance: ObjectT, name: str, value: Any) -> None:
            return object.__setattr__(instance, name, self.__handler.set(name, value))

        def __delattr__(instance: ObjectT, name: str) -> None:
            value: Any = object.__getattribute__(instance, name)
            object.__delattr__(instance, name)
            self.__handler.delete(name, value)

        def __dir__(instance: ObjectT) -> Iterable[str]:
            return sorted(set(dir(self.__superclass) + list(instance.__dict__.keys())))

        return new_class(
            name=self.__superclass.__name__ + self.__PROXY_CLASS_NAME_SUFFIX,
            bases=(self.__superclass,),
            exec_body=lambda ns: ns.update(
                __getattribute__=__getattribute__,
                __setattr__=__setattr__,
                __delattr__=__delattr__,
                __dir__=__dir__,
            ),
        )(*args, **kwargs)
