from dataclasses import dataclass

from spakky.aop.advisor import AdvisorT, AsyncAdvisorT
from spakky.core.annotation import ClassAnnotation


@dataclass
class Order(ClassAnnotation):
    order: int

    def __call__(self, obj: AdvisorT | AsyncAdvisorT) -> AdvisorT | AsyncAdvisorT:
        return super().__call__(obj)
