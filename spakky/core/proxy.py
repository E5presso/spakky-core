from abc import ABC, abstractmethod
from functools import wraps
from inspect import getmembers, iscoroutinefunction, isfunction
from types import FunctionType, MethodType, new_class
from typing import Any, Generic, Iterable, Protocol, final, runtime_checkable

from spakky.core.constants import DYNAMIC_PROXY_CLASS_NAME_SUFFIX
from spakky.core.types import AsyncFunc, Func, ObjectT


@runtime_checkable
class IProxyHandler(Protocol):
    @abstractmethod
    def call(
        self,
        func: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...

    @abstractmethod
    async def call_async(
        self,
        func: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any: ...

    @abstractmethod
    def get(self, name: str) -> Any: ...

    @abstractmethod
    def set(self, name: str, value: Any) -> None: ...

    @abstractmethod
    def delete(self, name: str) -> None: ...

    @abstractmethod
    def proxy_dir(self) -> Iterable[str]: ...


class AbstractProxyHandler(IProxyHandler, ABC):
    _target: object

    def __init__(self, target: object) -> None:
        self._target = target

    def call(
        self,
        func: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return MethodType(func, self._target)(*args, **kwargs)

    async def call_async(
        self,
        func: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return await MethodType(func, self._target)(*args, **kwargs)

    def get(self, name: str) -> Any:
        return getattr(self._target, name)

    def set(self, name: str, value: Any) -> None:
        return setattr(self._target, name, value)

    def delete(self, name: str) -> None:
        return delattr(self._target, name)

    @final
    def proxy_dir(self) -> Iterable[str]:
        return dir(self._target)


class ProxyFactory(Generic[ObjectT]):
    __type: type[ObjectT]
    __functions: dict[str, FunctionType]
    __handler: IProxyHandler

    def __init__(
        self,
        type_: type[ObjectT],
        handler: IProxyHandler,
    ) -> None:
        self.__type = type_
        self.__functions = {
            name: func for name, func in getmembers(self.__type, isfunction)
        }
        self.__handler = handler

    def __proxy_getattribute__(self, name: str) -> Any:
        if name not in self.__functions:
            return self.__proxy_getattr__(name)
        func = self.__functions[name]
        if iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await self.__proxy_call_async__(func, *args, **kwargs)

            return async_wrapper

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.__proxy_call__(func, *args, **kwargs)

        return wrapper

    def __proxy_call__(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        return self.__handler.call(func=method, *args, **kwargs)

    async def __proxy_call_async__(
        self, method: AsyncFunc, *args: Any, **kwargs: Any
    ) -> Any:
        return await self.__handler.call_async(func=method, *args, **kwargs)

    def __proxy_getattr__(self, name: str) -> Any:
        return self.__handler.get(name=name)

    def __proxy_setattr__(self, name: str, value: Any) -> None:
        return self.__handler.set(name=name, value=value)

    def __proxy_delattr__(self, name: str) -> None:
        return self.__handler.delete(name=name)

    def __proxy_dir__(self) -> Iterable[str]:
        return self.__handler.proxy_dir()

    def __proxy_init__(self) -> None:
        return

    def create(self) -> ObjectT:
        return new_class(
            name=self.__type.__name__ + DYNAMIC_PROXY_CLASS_NAME_SUFFIX,
            bases=(self.__type,),
            exec_body=lambda ns: ns.update(
                __getattribute__=self.__proxy_getattribute__,
                __setattr__=self.__proxy_setattr__,
                __delattr__=self.__proxy_delattr__,
                __dir__=self.__proxy_dir__,
                __init__=self.__proxy_init__,
            ),
        )()
