from dataclasses import dataclass, field
from spakky.framework.context.autowired import Autowired
from spakky.framework.core.generic import T_OBJ
from spakky.framework.core.annotation import Annotation


@dataclass
class Component(Annotation):
    autowired: dict[str, type] = field(init=False, default_factory=dict)

    def __call__(self, obj: T_OBJ) -> T_OBJ:
        autowired: Autowired | None = Autowired.get_annotation(obj.__init__)
        if autowired is not None:
            self.autowired = autowired.dependencies
        return self.set_annotation(obj)
