import sys
from types import MethodType
from typing import Any, Sequence
from inspect import ismethod, getmembers, iscoroutinefunction
from logging import Logger

from spakky.aop.advisor import Advisor, AsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.interfaces.aspect import IAspect, IAsyncAspect
from spakky.core.proxy import ProxyFactory, ProxyHandler
from spakky.core.types import AsyncFunc, Func
from spakky.pod.annotations.order import Order
from spakky.pod.annotations.pod import Pod
from spakky.pod.interfaces.container import IContainer
from spakky.pod.interfaces.post_processor import IPostProcessor


class AspectProxyHandler(ProxyHandler):
    __advisor_map: dict[MethodType | Func, MethodType | Advisor]
    __async_advisor_map: dict[MethodType | AsyncFunc, MethodType | AsyncAdvisor]

    def __init__(self, instance: object, aspects: Sequence[object]) -> None:
        super().__init__()
        self.__advisor_map = {}
        self.__async_advisor_map = {}
        for _, method in getmembers(instance, ismethod):
            if iscoroutinefunction(method):
                runnable = method
                for aspect in [
                    x
                    for x in aspects
                    if isinstance(x, IAsyncAspect) and AsyncAspect.get(x).matches(method)
                ]:
                    runnable = AsyncAdvisor(aspect, runnable)
                self.__async_advisor_map[method] = runnable
            else:
                runnable = method
                for aspect in [
                    x
                    for x in aspects
                    if isinstance(x, IAspect) and Aspect.get(x).matches(method)
                ]:
                    runnable = Advisor(aspect, runnable)
                self.__advisor_map[method] = runnable

    def call(self, method: Func, *args: Any, **kwargs: Any) -> Any:
        return self.__advisor_map[method](*args, **kwargs)

    async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
        return await self.__async_advisor_map[method](*args, **kwargs)


@Pod()
class AspectPostProcessor(IPostProcessor):
    __logger: Logger
    __cache: dict[type, object]
    __container: IContainer

    def __init__(self, container: IContainer, logger: Logger) -> None:
        super().__init__()
        self.__cache = {}
        self.__container = container
        self.__logger = logger

    def __set_cache(self, type_: type, obj: object) -> object:
        self.__cache[type_] = obj
        return obj

    def __get_cache(self, type_: type) -> object | None:
        return self.__cache.get(type_, None)

    def post_process(self, pod: object) -> object:
        if (cached := self.__get_cache(type(pod))) is not None:
            return cached
        if Aspect.exists(pod) or AsyncAspect.exists(pod):
            return self.__set_cache(type(pod), pod)
        if not Pod.exists(pod):
            return self.__set_cache(type(pod), pod)

        def selector(x: Pod) -> bool:
            return (
                Aspect.exists(x.target)
                and Aspect.get(x.target).matches(pod)
                or AsyncAspect.exists(x.target)
                and AsyncAspect.get(x.target).matches(pod)
            )

        matched: Sequence[object] = list(self.__container.find(selector))
        if not any(matched):
            return self.__set_cache(type(pod), pod)
        matched.sort(
            key=lambda x: Order.get_or_default(x, Order(sys.maxsize)).order,
            reverse=True,
        )

        self.__logger.debug(
            (
                f"[{type(self).__name__}] "
                f"{[f"{type(x).__name__}" for x in matched]!r} "
                f"-> {type(pod).__name__!r}"
            )
        )
        return self.__set_cache(
            type(pod),
            ProxyFactory(
                superclass=type(pod),
                instance=pod,
                handler=AspectProxyHandler(pod, matched),
            ).create(),
        )
