from typing import Any
from inspect import ismethod, getmembers
from logging import Logger

from spakky.aop.advice import Advice, AsyncAdvice, AsyncPointcut, Pointcut
from spakky.dependency.autowired import autowired
from spakky.dependency.interfaces.dependency_container import IDependencyContainer
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)
from spakky.dependency.plugin import PostProcessor


@PostProcessor()
class AspectDependencyPostPrecessor(IDependencyPostProcessor):
    __logger: Logger

    @autowired
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def process_dependency(self, container: IDependencyContainer, dependency: Any) -> Any:
        for name, method in getmembers(dependency, ismethod):
            if Pointcut.contains(method):
                pointcuts: list[Pointcut] = Pointcut.all(method)
                for pointcut in pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(pointcut).__name__} -> {method.__qualname__}"
                    )
                    advice: Advice = container.get(required_type=pointcut.advice)
                    method = advice(method)
                setattr(dependency, name, method)
            if AsyncPointcut.contains(method):
                async_pointcuts: list[AsyncPointcut] = AsyncPointcut.all(method)
                for async_pointcut in async_pointcuts:
                    self.__logger.info(
                        f"[{type(self).__name__}] {type(async_pointcut).__name__} -> {method.__qualname__}"
                    )
                    async_advice: AsyncAdvice = container.get(
                        required_type=async_pointcut.advice
                    )
                    method = async_advice(method)
                setattr(dependency, name, method)
        return dependency
