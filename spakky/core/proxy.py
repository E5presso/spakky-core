from abc import ABC, abstractmethod
from functools import wraps
from inspect import iscoroutinefunction, ismethod
from types import new_class
from typing import Any, ClassVar, Generic, Iterable, Protocol, runtime_checkable

from spakky.core.constants import DYNAMIC_PROXY_CLASS_NAME_SUFFIX
from spakky.core.types import AsyncFunc, Func, ObjectT


@runtime_checkable
class IProxyHandler(Protocol):
    @abstractmethod
    def call(
        self,
        target: object,
        method: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...

    @abstractmethod
    async def call_async(
        self,
        target: object,
        method: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...

    @abstractmethod
    def get(self, target: object, name: str) -> Any: ...

    @abstractmethod
    def set(self, target: object, name: str, value: Any) -> None: ...

    @abstractmethod
    def delete(self, target: object, name: str) -> None: ...


class AbstractProxyHandler(IProxyHandler, ABC):
    def call(
        self,
        target: object,
        method: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return method(*args, **kwargs)

    async def call_async(
        self,
        target: object,
        method: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return await method(*args, **kwargs)

    def get(self, target: object, name: str) -> Any:
        return getattr(target, name)

    def set(self, target: object, name: str, value: Any) -> None:
        return setattr(target, name, value)

    def delete(self, target: object, name: str) -> None:
        return delattr(target, name)


class ProxyFactory(Generic[ObjectT]):
    ATTRIBUTES_TO_IGNORE: ClassVar[Iterable[str]] = [
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

    _type: type[ObjectT]
    _target: ObjectT
    _handler: IProxyHandler

    def __init__(
        self,
        target: ObjectT,
        handler: IProxyHandler,
    ) -> None:
        self._type = type(target)
        self._target = target
        self._handler = handler

    def __proxy_getattribute__(self, name: str) -> Any:
        value: Any = object.__getattribute__(self._target, name)
        if ismethod(value):
            if iscoroutinefunction(value):

                @wraps(value)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    return await self.__proxy_call_async__(value, *args, **kwargs)

                return async_wrapper

            @wraps(value)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                return self.__proxy_call__(value, *args, **kwargs)

            return wrapper
        if name in self.ATTRIBUTES_TO_IGNORE:
            return value
        return self.__proxy_getattr__(name)

    def __proxy_call__(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        return self._handler.call(
            target=self._target,
            method=method,
            *args,
            **kwargs,
        )

    async def __proxy_call_async__(
        self, method: AsyncFunc, *args: Any, **kwargs: Any
    ) -> Any:
        return await self._handler.call_async(
            target=self._target,
            method=method,
            *args,
            **kwargs,
        )

    def __proxy_getattr__(self, name: str) -> Any:
        return self._handler.get(target=self._target, name=name)

    def __proxy_setattr__(self, name: str, value: Any) -> None:
        return self._handler.set(target=self._target, name=name, value=value)

    def __proxy_delattr__(self, name: str) -> None:
        return self._handler.delete(target=self._target, name=name)

    def __proxy_dir__(self) -> Iterable[str]:
        return sorted(set(dir(self._target) + list(self._type.__dict__.keys())))

    def __proxy_init__(self) -> None:
        return

    def create(self) -> ObjectT:
        return new_class(
            name=self._type.__name__ + DYNAMIC_PROXY_CLASS_NAME_SUFFIX,
            bases=(self._type,),
            exec_body=lambda ns: ns.update(
                __getattribute__=self.__proxy_getattribute__,
                __setattr__=self.__proxy_setattr__,
                __delattr__=self.__proxy_delattr__,
                __dir__=self.__proxy_dir__,
                __init__=self.__proxy_init__,
            ),
        )()
