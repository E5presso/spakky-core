from typing import Any
from inspect import getmembers
from logging import Logger

from spakky.aop.advice import (
    AbstractAdvice,
    AbstractAsyncAdvice,
    AsyncPointcut,
    Pointcut,
)
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.bean.interfaces.post_processor import IBeanPostProcessor


@Bean()
class AspectDependencyPostPrecessor(IBeanPostProcessor):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def post_process(self, container: IBeanContainer, bean: Any) -> Any:
        for name, member in getmembers(bean):
            if Pointcut.contains(member):
                pointcuts: list[Pointcut] = Pointcut.all(member)
                for pointcut in pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(pointcut).__name__} -> {member.__qualname__}"
                    )
                    advice: AbstractAdvice = container.get(required_type=pointcut.advice)
                    member = advice(pointcut, member)
                setattr(bean, name, member)
            if AsyncPointcut.contains(member):
                async_pointcuts: list[AsyncPointcut] = AsyncPointcut.all(member)
                for async_pointcut in async_pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(async_pointcut).__name__} -> {member.__qualname__}"
                    )
                    async_advice: AbstractAsyncAdvice = container.get(
                        required_type=async_pointcut.advice
                    )
                    member = async_advice(async_pointcut, member)
                setattr(bean, name, member)
        return bean
