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
        for _, method in getmembers(bean):
            if (advice := Before.single_or_none(self.advisor.before)) is not None:
                if advice.matches(method):
                    return True
            if (
                advice := AfterReturning.single_or_none(self.advisor.after_returning)
            ) is not None:
                if advice.matches(method):
                    return True
            if (
                advice := AfterRaising.single_or_none(self.advisor.after_raising)
            ) is not None:
                if advice.matches(method):
                    return True
            if (advice := After.single_or_none(self.advisor.after)) is not None:
                if advice.matches(method):
                    return True
            if (advice := Around.single_or_none(self.advisor.around)) is not None:
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
        for _, method in getmembers(bean):
            if (advice := Before.single_or_none(self.advisor.before_async)) is not None:
                if advice.matches(method):
                    return True
            if (
                advice := AfterReturning.single_or_none(
                    self.advisor.after_returning_async
                )
            ) is not None:
                if advice.matches(method):
                    return True
            if (
                advice := AfterRaising.single_or_none(self.advisor.after_raising_async)
            ) is not None:
                if advice.matches(method):
                    return True
            if (advice := After.single_or_none(self.advisor.after_async)) is not None:
                if advice.matches(method):
                    return True
            if (advice := Around.single_or_none(self.advisor.around_async)) is not None:
                if advice.matches(method):
                    return True
        return False
