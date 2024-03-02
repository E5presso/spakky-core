from inspect import ismethod, getmembers
from dataclasses import field, dataclass

from spakky.aop.advice import After, AfterRaising, AfterReturning, Around, Before
from spakky.aop.advisor import AdvisorT, AsyncAdvisorT, IAdvisor, IAsyncAdvisor
from spakky.bean.bean import Bean
from spakky.core.annotation import AnnotationNotFoundError


@dataclass
class Aspect(Bean):
    advisor: type[IAdvisor] = field(init=False)

    def __call__(self, obj: AdvisorT) -> AdvisorT:
        self.advisor = obj
        return super().__call__(obj)

    def matches(self, bean: object) -> bool:
        for _, method in getmembers(bean, ismethod):
            try:
                return (
                    Before.single(self.advisor.before).matches(method)
                    or AfterReturning.single(self.advisor.after_returning).matches(method)
                    or AfterRaising.single(self.advisor.after_raising).matches(method)
                    or After.single(self.advisor.after).matches(method)
                    or Around.single(self.advisor.around).matches(method)
                )
            except AnnotationNotFoundError:
                return False
        return False


@dataclass
class AsyncAspect(Bean):
    advisor: type[IAsyncAdvisor] = field(init=False)

    def __call__(self, obj: AsyncAdvisorT) -> AsyncAdvisorT:
        self.advisor = obj
        return super().__call__(obj)

    def matches(self, bean: object) -> bool:
        for _, method in getmembers(bean, ismethod):
            try:
                return (
                    Before.single(self.advisor.before_async).matches(method)
                    or AfterReturning.single(self.advisor.after_returning_async).matches(
                        method
                    )
                    or AfterRaising.single(self.advisor.after_raising_async).matches(
                        method
                    )
                    or After.single(self.advisor.after_async).matches(method)
                    or Around.single(self.advisor.around_async).matches(method)
                )
            except AnnotationNotFoundError:
                return False
        return False
