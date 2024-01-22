from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation
from spakky.core.generics import ClassT
from spakky.dependency.autowired import Autowired


@dataclass
class Dependency(ClassAnnotation):
    dependencies: dict[str, type] | None = field(init=False, default=None)

    def __call__(self, obj: ClassT) -> ClassT:
        autowired: Autowired | None = Autowired.single_or_none(obj.__init__)
        if autowired is not None:
            self.dependencies = autowired.dependencies
        return super().__call__(obj)
