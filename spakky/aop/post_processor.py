import sys
from types import MethodType
from typing import Any, Sequence
from inspect import ismethod, getmembers, iscoroutinefunction
from logging import Logger

from spakky.aop.advisor import Advisor, AsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect, IAspect, IAsyncAspect
from spakky.application.interfaces.container import IPodContainer
from spakky.application.interfaces.post_processor import IPodPostProcessor
from spakky.core.proxy import AbstractProxyHandler, ProxyFactory
from spakky.core.types import AsyncFunc, Func
from spakky.pod.order import Order
from spakky.pod.pod import Pod


class AspectProxyHandler(AbstractProxyHandler):
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


@Order(0)
class AspectPostProcessor(IPodPostProcessor):
    __logger: Logger
    __cache: dict[type, object]

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger
        self.__cache = {}

    def __set_cache(self, type_: type, obj: object) -> object:
        self.__cache[type_] = obj
        return obj

    def __get_cache(self, type_: type) -> object | None:
        return self.__cache.get(type_, None)

    def post_process(self, container: IPodContainer, pod: object) -> object:
        if (cached := self.__get_cache(type(pod))) is not None:
            return cached
        if Aspect.exists(pod) or AsyncAspect.exists(pod):
            return self.__set_cache(type(pod), pod)
        if not Pod.exists(pod):
            return self.__set_cache(type(pod), pod)

        def selector(x: Pod) -> bool:
            return (
                Aspect.exists(x.obj)
                and Aspect.get(x.obj).matches(pod)
                or AsyncAspect.exists(x.obj)
                and AsyncAspect.get(x.obj).matches(pod)
            )

        matched: Sequence[object] = list(container.find(selector).values())
        if not any(matched):
            return self.__set_cache(type(pod), pod)
        matched.sort(
            key=lambda x: Order.get_or_default(x, Order(sys.maxsize)).order,
            reverse=True,
        )
        # pylint: disable=line-too-long
        self.__logger.info(
            f"[{type(self).__name__}] {[f'{type(x).__name__}({Order.get_or_default(x, Order(sys.maxsize)).order})' for x in matched]!r} -> {type(pod).__name__}"
        )
        return self.__set_cache(
            type(pod),
            ProxyFactory(
                superclass=type(pod),
                instance=pod,
                handler=AspectProxyHandler(pod, matched),
            ).create(),
        )
