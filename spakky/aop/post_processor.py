from typing import Any
from inspect import ismethod, getmembers
from logging import Logger

from spakky.aop.advice import Advice, AsyncAdvice, AsyncPointcut, Pointcut
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor


class AspectDependencyPostPrecessor(IBeanPostProcessor):
    __logger: Logger

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def process_bean(self, container: IBeanContainer, bean: Any) -> Any:
        for name, method in getmembers(bean, ismethod):
            if Pointcut.contains(method):
                pointcuts: list[Pointcut] = Pointcut.all(method)
                for pointcut in pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(pointcut).__name__} -> {method.__qualname__}"
                    )
                    advice: Advice = container.get(required_type=pointcut.advice)
                    method = advice(pointcut, method)
                setattr(bean, name, method)
            if AsyncPointcut.contains(method):
                async_pointcuts: list[AsyncPointcut] = AsyncPointcut.all(method)
                for async_pointcut in async_pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(async_pointcut).__name__} -> {method.__qualname__}"
                    )
                    async_advice: AsyncAdvice = container.get(
                        required_type=async_pointcut.advice
                    )
                    method = async_advice(async_pointcut, method)
                setattr(bean, name, method)
        return bean
