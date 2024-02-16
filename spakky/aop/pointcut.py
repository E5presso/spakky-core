from typing import ClassVar
from dataclasses import dataclass

from spakky.aop.advisor import Advisor, AsyncAdvisor
from spakky.core.annotation import FunctionAnnotation


@dataclass
class Pointcut(FunctionAnnotation):
    advisor: ClassVar[type[Advisor]]


@dataclass
class AsyncPointcut(FunctionAnnotation):
    advisor: ClassVar[type[AsyncAdvisor]]
