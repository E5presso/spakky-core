import sys
from typing import Any, Sequence, cast
from logging import Logger

from spakky.aop.aspect import Aspect, AsyncAspect, IAspect, IAsyncAspect
from spakky.aop.order import Order
from spakky.application.interfaces.container import IContainer
from spakky.application.interfaces.processor import IPostProcessor
from spakky.core.proxy import AbstractProxyHandler, ProxyFactory
from spakky.core.types import AsyncFunc, Func
from spakky.injectable.injectable import Injectable, UnknownType


class _Runnable:
    instance: IAspect
    next: Func

    def __init__(self, instance: IAspect, next: Func) -> None:
        self.instance = instance
        self.next = next

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.instance.before(*args, **kwargs)
        try:
            result = self.instance.around(self.next, *args, **kwargs)
            self.instance.after_returning(result)
            return result
        except Exception as e:
            self.instance.after_raising(e)
            raise
        finally:
            self.instance.after()


class _AsyncRunnable:
    instance: IAsyncAspect
    next: AsyncFunc

    def __init__(self, instance: IAsyncAspect, next: AsyncFunc) -> None:
        self.instance = instance
        self.next = next

    def __getattr__(self, name: str) -> Any:
        return getattr(self.next, name)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        await self.instance.before_async(*args, **kwargs)
        try:
            result = await self.instance.around_async(self.next, *args, **kwargs)
            await self.instance.after_returning_async(result)
            return result
        except Exception as e:
            await self.instance.after_raising_async(e)
            raise
        finally:
            await self.instance.after_async()


class AspectProxyHandler(AbstractProxyHandler):
    __container: IContainer
    __aspects: Sequence[type[IAspect | IAsyncAspect]]

    def __init__(
        self,
        container: IContainer,
        aspects: Sequence[type[IAspect | IAsyncAspect]],
    ) -> None:
        super().__init__()
        self.__container = container
        self.__aspects = aspects

    def call(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        aspects: Sequence[type[IAspect]] = [
            x for x in self.__aspects if issubclass(x, IAspect)
        ]
        matched: Sequence[type[IAspect]] = [
            x for x in aspects if Aspect.get(x).matches(method)
        ]
        runnable: Func = method
        for aspect in matched:
            runnable = _Runnable(self.__container.get(type_=aspect), runnable)
        return runnable(*args, **kwargs)

    async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        aspects: Sequence[type[IAsyncAspect]] = [
            x for x in self.__aspects if issubclass(x, IAsyncAspect)
        ]
        matched: Sequence[type[IAsyncAspect]] = [
            x for x in aspects if AsyncAspect.get(x).matches(method)
        ]
        runnable: AsyncFunc = method
        for aspect in matched:
            runnable = _AsyncRunnable(self.__container.get(type_=aspect), runnable)
        return await runnable(*args, **kwargs)


class AspectPostProcessor(IPostProcessor):
    __logger: Logger
    __cache: dict[type, object]

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger
        self.__cache = {}

    def __set_cache(self, type_: type, injectable: object) -> object:
        self.__cache[type_] = injectable
        return injectable

    def __get_cache(self, type_: type) -> object | None:
        return self.__cache.get(type_, None)

    def post_process(self, container: IContainer, injectable: object) -> object:
        if (cached := self.__get_cache(type(injectable))) is not None:
            return cached
        if Aspect.contains(injectable) or AsyncAspect.contains(injectable):
            return self.__set_cache(type(injectable), injectable)
        injectable_annotation: Injectable | None = Injectable.get_or_none(injectable)
        if injectable_annotation is None:
            self.__set_cache(type(injectable), injectable)
            return injectable
        matched_aspects: Sequence[type[IAspect | IAspect]] = []
        aspects: Sequence[type] = container.filter_injectable_types(
            lambda x: Aspect.contains(x) or AsyncAspect.contains(x)
        )
        for aspect in aspects:
            aspect_annotation: Aspect | None = Aspect.get_or_none(aspect)
            async_aspect: AsyncAspect | None = AsyncAspect.get_or_none(aspect)
            if aspect_annotation is not None and aspect_annotation.matches(injectable):
                matched_aspects.append(cast(type[IAspect], aspect))
                continue
            if async_aspect is not None and async_aspect.matches(injectable):
                matched_aspects.append(cast(type[IAspect], aspect))
                continue
        if not any(matched_aspects):
            self.__cache[type(injectable)] = injectable
            return injectable
        matched_aspects.sort(
            key=lambda x: Order.get_or_default(x, Order(sys.maxsize)).order,
            reverse=True,
        )
        # pylint: disable=line-too-long
        self.__logger.info(
            f"[{type(self).__name__}] {[f'{x.__name__}({Order.get_or_default(x, Order(sys.maxsize)).order})' for x in matched_aspects]!r} -> {type(injectable).__name__}"
        )
        dependencies: dict[str, object] = {}
        for name, required_type in injectable_annotation.dependencies.items():
            if required_type == UnknownType:
                dependencies[name] = container.get(name=name)
                continue
            dependencies[name] = container.get(type_=required_type)
        return self.__set_cache(
            type(injectable),
            ProxyFactory(
                superclass=type(injectable),
                handler=AspectProxyHandler(container, matched_aspects),
            ).create(**dependencies),
        )
