from inspect import getmembers
from dataclasses import field, dataclass

from spakky.aop.advice import After, AfterRaising, AfterReturning, Around, Before
from spakky.aop.advisor import AdvisorT, AsyncAdvisorT, IAdvisor, IAsyncAdvisor
from spakky.bean.bean import Bean


@dataclass
class Aspect(Bean):
    advisor: type[IAdvisor] = field(init=False)

    def __call__(self, obj: AdvisorT) -> AdvisorT:
        self.advisor = obj
        return super().__call__(obj)

    def matches(self, bean: object) -> bool:
        for _, method in getmembers(bean, callable):
            for annotation, target_method in {
                Before: self.advisor.before,
                AfterReturning: self.advisor.after_returning,
                AfterRaising: self.advisor.after_raising,
                After: self.advisor.after,
                Around: self.advisor.around,
            }.items():
                if (advice := annotation.single_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False


@dataclass
class AsyncAspect(Bean):
    advisor: type[IAsyncAdvisor] = field(init=False)

    def __call__(self, obj: AsyncAdvisorT) -> AsyncAdvisorT:
        self.advisor = obj
        return super().__call__(obj)

    def matches(self, bean: object) -> bool:
        for _, method in getmembers(bean, callable):
            for annotation, target_method in {
                Before: self.advisor.before_async,
                AfterReturning: self.advisor.after_returning_async,
                AfterRaising: self.advisor.after_raising_async,
                After: self.advisor.after_async,
                Around: self.advisor.around_async,
            }.items():
                if (advice := annotation.single_or_none(target_method)) is not None:
                    if advice.matches(method):
                        return True
        return False
