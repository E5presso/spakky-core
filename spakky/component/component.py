from enum import Enum, auto
from typing import Callable
from inspect import Parameter, signature
from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation
from spakky.core.generics import ClassT
from spakky.utils.casing import pascal_to_snake


class ProvidingType(Enum):
    SINGLETON = auto()
    FACTORY = auto()


class Unknown:
    ...


@dataclass
class Component(ClassAnnotation):
    providing_type: ProvidingType = field(kw_only=True, default=ProvidingType.SINGLETON)
    name: str = field(init=False, default="")
    dependencies: dict[str, type] = field(init=False, default_factory=dict[str, type])

    def __call__(self, obj: ClassT) -> ClassT:
        constructor: Callable[..., None] = obj.__init__
        self.name = pascal_to_snake(obj.__name__)

        # Ignore self instance pointer argument in dependencies map
        parameters: list[Parameter] = list(signature(constructor).parameters.values())[1:]

        for parameter in parameters:
            if parameter.annotation == Parameter.empty:
                # Mark unknown type (no type annotated)
                self.dependencies[parameter.name] = Unknown
                continue
            self.dependencies[parameter.name] = parameter.annotation
        return super().__call__(obj)
