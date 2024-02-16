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
                pointcut: Pointcut = Pointcut.single(method)
                advisor: Advisor = container.get(required_type=pointcut.advisor)
                setattr(dependency, name, advisor(method))
            if AsyncPointcut.contains(method):
                async_pointcut: AsyncPointcut = AsyncPointcut.single(method)
                async_advisor: AsyncAdvisor = container.get(
                    required_type=async_pointcut.advisor
                )
                setattr(dependency, name, async_advisor(method))
        return dependency
