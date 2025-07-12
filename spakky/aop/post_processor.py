import sys
from logging import Logger
from typing import Any, Sequence

from spakky.aop.advisor import Advisor, AsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.interfaces.aspect import IAspect, IAsyncAspect
from spakky.core.proxy import AbstractProxyHandler, ProxyFactory
from spakky.core.types import AsyncFunc, Func
from spakky.pod.annotations.order import Order
from spakky.pod.annotations.pod import Pod
from spakky.pod.interfaces.container import IContainer
from spakky.pod.interfaces.post_processor import IPostProcessor


class AspectProxyHandler(AbstractProxyHandler):
    __advisors_cache: dict[Func, Func | Advisor]
    __async_advisors_cache: dict[AsyncFunc, AsyncFunc | AsyncAdvisor]
    __aspects: Sequence[object]

    def __init__(self, aspects: Sequence[object]) -> None:
        self.__advisors_cache = {}
        self.__async_advisors_cache = {}
        self.__aspects = aspects

    def call(
        self,
        target: object,
        method: Func,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if method not in self.__advisors_cache:
            runnable = method
            candidates = [
                x
                for x in self.__aspects
                if isinstance(x, IAspect) and Aspect.get(x).matches(method)
            ]
            for candidate in candidates:
                runnable = Advisor(candidate, runnable)
            self.__advisors_cache[method] = runnable
        return self.__advisors_cache[method](*args, **kwargs)

    async def call_async(
        self,
        target: object,
        method: AsyncFunc,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if method not in self.__async_advisors_cache:
            runnable = method
            candidates = [
                x
                for x in self.__aspects
                if isinstance(x, IAsyncAspect) and AsyncAspect.get(x).matches(method)
            ]
            for candidate in candidates:
                runnable = AsyncAdvisor(candidate, runnable)
            self.__async_advisors_cache[method] = runnable
        return await self.__async_advisors_cache[method](*args, **kwargs)


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

        matched_aspects: Sequence[object] = list(self.__container.find(selector))
        if not any(matched_aspects):
            # No matching aspects found, return the pod as is
            return self.__set_cache(type(pod), pod)

        matched_aspects.sort(
            key=lambda x: Order.get_or_default(
                obj=x,
                default=Order(sys.maxsize),
            ).order,
            reverse=True,
        )
        self.__logger.debug(
            f"[{type(self).__name__}] {[f'{type(x).__name__}' for x in matched_aspects]!r} -> {type(pod).__name__!r}"
        )
        return self.__set_cache(
            type(pod),
            ProxyFactory(
                target=pod,
                handler=AspectProxyHandler(matched_aspects),
            ).create(),
        )
