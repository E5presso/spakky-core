from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation
from spakky.dependency.autowired import Autowired


@dataclass
class Dependency(ClassAnnotation):
    dependencies: dict[str, type] = field(init=False, default_factory=dict[str, type])

    def __call__(self, obj: type) -> type:
        autowired: Autowired | None = Autowired.single_or_none(obj.__init__)
        if autowired is not None:
            self.dependencies = autowired.dependencies
        return super().__call__(obj)
