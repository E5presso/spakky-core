from typing import TypeVar, Callable, TypeAlias
from inspect import Parameter, signature
from dataclasses import field, dataclass

from spakky.bean.autowired import Autowired
from spakky.bean.error import SpakkyBeanError
from spakky.bean.provider import Provider, ProvidingType
from spakky.core.annotation import ClassAnnotation, FunctionAnnotation
from spakky.core.generics import ClassT
from spakky.utils.casing import pascal_to_snake

BeanFactoryType: TypeAlias = Callable[[], object]
BeanFactoryT = TypeVar("BeanFactoryT", bound=BeanFactoryType)


class ReturnAnnotationNotFoundInBeanFactoryError(SpakkyBeanError):
    message = "Cannot find return annotation in bean factory"


@dataclass
class Bean(ClassAnnotation):
    name: str = field(init=False, default="")
    dependencies: dict[str, type[object]] = field(
        init=False, default_factory=dict[str, type[object]]
    )
    providing_type: ProvidingType = field(init=False, default=ProvidingType.SINGLETON)

    def __call__(self, obj: ClassT) -> ClassT:
        constructor: Callable[..., None] = obj.__init__
        self.name = pascal_to_snake(obj.__name__)
        autowired_annotation: Autowired | None = Autowired.single_or_none(constructor)
        provider_annotation: Provider | None = Provider.single_or_none(obj)
        if autowired_annotation is not None:
            self.dependencies = autowired_annotation.dependencies
        if provider_annotation is not None:
            self.providing_type = provider_annotation.providing_type
        return super().__call__(obj)


@dataclass
class BeanFactory(FunctionAnnotation):
    name: str = field(init=False)
    bean_type: type[object] = field(init=False)
    providing_type: ProvidingType = field(init=False, default=ProvidingType.SINGLETON)

    def __call__(self, obj: BeanFactoryT) -> BeanFactoryT:
        return_type: type = signature(obj).return_annotation
        if issubclass(return_type, Parameter.empty):
            raise ReturnAnnotationNotFoundInBeanFactoryError
        provider_annotation: Provider | None = Provider.single_or_none(obj)
        self.name = obj.__name__
        self.bean_type = return_type
        if provider_annotation is not None:
            self.providing_type = provider_annotation.providing_type
        return super().__call__(obj)
