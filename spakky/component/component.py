from typing import Callable
from dataclasses import field, dataclass

from spakky.component.autowired import Autowired
from spakky.core.annotation import ClassAnnotation
from spakky.core.generics import ClassT
from spakky.utils.casing import pascal_to_snake


class Unknown:
    ...


@dataclass
class Component(ClassAnnotation):
    name: str = field(init=False, default="")
    dependencies: dict[str, type] = field(init=False, default_factory=dict[str, type])

    def __call__(self, obj: ClassT) -> ClassT:
        constructor: Callable[..., None] = obj.__init__
        self.name = pascal_to_snake(obj.__name__)

        autowired_annotation: Autowired | None = Autowired.single_or_none(constructor)
        if autowired_annotation is not None:
            self.dependencies = autowired_annotation.dependencies
        return super().__call__(obj)
