from typing import TypeVar, Callable, TypeAlias
from inspect import Parameter, signature
from dataclasses import field, dataclass

from spakky.bean.autowired import Autowired
from spakky.bean.error import SpakkyBeanError
from spakky.core.annotation import ClassAnnotation, FunctionAnnotation
from spakky.core.types import ClassT
from spakky.utils.casing import pascal_to_snake

BeanFactoryType: TypeAlias = Callable[[], object]
BeanFactoryT = TypeVar("BeanFactoryT", bound=BeanFactoryType)


class ReturnAnnotationNotFoundInBeanFactoryError(SpakkyBeanError):
    message = "Cannot find return annotation in bean factory"


@dataclass
class Bean(ClassAnnotation):
    bean_name: str = field(kw_only=True, default="")
    dependencies: dict[str, type[object]] = field(init=False, default_factory=dict)

    def __call__(self, obj: ClassT) -> ClassT:
        constructor: Callable[..., None] = obj.__init__
        if not self.bean_name:
            self.bean_name = pascal_to_snake(obj.__name__)
        autowired_annotation: Autowired | None = Autowired.single_or_none(constructor)
        if autowired_annotation is not None:
            self.dependencies = autowired_annotation.dependencies
        return super().__call__(obj)


@dataclass
class BeanFactory(FunctionAnnotation):
    bean_name: str = field(kw_only=True, default="")
    bean_type: type[object] = field(init=False)

    def __call__(self, obj: BeanFactoryT) -> BeanFactoryT:
        return_type: type = signature(obj).return_annotation
        if return_type == Parameter.empty:
            raise ReturnAnnotationNotFoundInBeanFactoryError
        if not self.bean_name:
            self.bean_name = obj.__name__
        self.bean_type = return_type
        return super().__call__(obj)
