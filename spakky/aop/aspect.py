from dataclasses import dataclass
from inspect import getmembers

from spakky.aop.error import AspectInheritanceError
from spakky.aop.interfaces.aspect import IAspect, IAsyncAspect
from spakky.aop.pointcut import (
    AbstractPointCut,
    After,
    AfterRaising,
    AfterReturning,
    Around,
    Before,
)
from spakky.core.types import AsyncFunc, Func
from spakky.pod.annotations.pod import Pod, is_class_pod


@dataclass(eq=False)
class Aspect(Pod):
    def matches(self, pod: object) -> bool:
        if not is_class_pod(self.target):
            raise AspectInheritanceError
        if not issubclass(self.target, IAspect):
            raise AspectInheritanceError
        pointcuts: dict[type[AbstractPointCut], Func] = {
            Before: self.target.before,
            AfterReturning: self.target.after_returning,
            AfterRaising: self.target.after_raising,
            After: self.target.after,
            Around: self.target.around,
        }
        if callable(pod):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(pod):
                        return True
        for _, method in getmembers(pod, callable):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False


@dataclass(eq=False)
class AsyncAspect(Pod):
    def matches(self, pod: object) -> bool:
        if not is_class_pod(self.target):
            raise AspectInheritanceError
        if not issubclass(self.target, IAsyncAspect):
            raise AspectInheritanceError
        pointcuts: dict[type[AbstractPointCut], AsyncFunc] = {
            Before: self.target.before_async,
            AfterReturning: self.target.after_returning_async,
            AfterRaising: self.target.after_raising_async,
            After: self.target.after_async,
            Around: self.target.around_async,
        }
        if callable(pod):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(pod):
                        return True
        for _, method in getmembers(pod, callable):
            for annotation, target_method in pointcuts.items():
                if (advice := annotation.get_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False
