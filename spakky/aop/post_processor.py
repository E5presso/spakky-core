from typing import Any
from inspect import ismethod, getmembers

from spakky.aop.advisor import Advisor, AsyncAdvisor
from spakky.aop.pointcut import AsyncPointcut, Pointcut
from spakky.dependency.interfaces.dependency_container import IDependencyContainer
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)


class AspectDependencyPostPrecessor(IDependencyPostProcessor):
    def process_dependency(self, container: IDependencyContainer, dependency: Any) -> Any:
        for name, method in getmembers(dependency, ismethod):
            if Pointcut.contains(method):
                pointcuts: list[Pointcut] = Pointcut.all(method)
                for async_pointcut in pointcuts:
                    advisor: Advisor = container.get(required_type=async_pointcut.advisor)
                    method = advisor(method)
                setattr(dependency, name, method)
            if AsyncPointcut.contains(method):
                async_pointcuts: list[AsyncPointcut] = AsyncPointcut.all(method)
                for async_pointcut in async_pointcuts:
                    async_advisor: AsyncAdvisor = container.get(
                        required_type=async_pointcut.advisor
                    )
                    method = async_advisor(method)
                setattr(dependency, name, method)
        return dependency
