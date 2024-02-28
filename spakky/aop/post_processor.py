from types import MethodType
from typing import Any, Sequence
from inspect import ismethod, getmembers, iscoroutinefunction
from logging import Logger

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor
from spakky.core.proxy import Enhancer, IMethodInterceptor


class AspectMethodInterceptor(IMethodInterceptor):
    __advisors: Sequence[object]

    def __init__(self, advisors: Sequence[object]) -> None:
        super().__init__()
        self.__advisors = advisors

    def intercept(
        self,
        method: MethodType,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if iscoroutinefunction(method):
            runnable = method
            for advisor in self.__advisors:
                runnable = AsyncAspect.single(advisor).to_runnable_aspect(
                    advisor,
                    runnable,
                )
            return runnable(*args, **kwargs)
        runnable = method
        for advisor in self.__advisors:
            runnable = Aspect.single(advisor).to_runnable_aspect(
                advisor,
                runnable,
            )
        return runnable(*args, **kwargs)


class AspectBeanPostProcessor(IBeanPostProcessor):
    __logger: Logger

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def post_process_bean(self, container: IBeanContainer, bean: object) -> object:
        if Aspect.contains(bean) or AsyncAspect.contains(bean):
            return bean
        advisors: Sequence[object] = container.where(
            lambda x: Aspect.contains(x) or AsyncAspect.contains(x)
        )
        matched_advisors: Sequence[object] = []
        for advisor in advisors:
            if Aspect.contains(advisor):
                if any(
                    method
                    for _, method in getmembers(bean, ismethod)
                    if Aspect.single(advisor).is_matched(method)
                ):
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(advisor).__name__} -> {type(bean).__name__}"
                    )
                    matched_advisors.append(advisor)
                    break
            if AsyncAspect.contains(advisor):
                if any(
                    method
                    for _, method in getmembers(bean, ismethod)
                    if AsyncAspect.single(advisor).is_matched(method)
                ):
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(advisor).__name__} -> {type(bean).__name__}"
                    )
                    matched_advisors.append(advisor)
                    break
        return Enhancer(
            superclass=type(bean),
            callback=AspectMethodInterceptor(advisors=matched_advisors),
        ).create()
