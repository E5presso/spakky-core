from dataclasses import dataclass

from spakky.dependency.component import Component
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)


@dataclass
class PostProcessor(Component):
    def __call__(
        self, obj: type[IDependencyPostProcessor]
    ) -> type[IDependencyPostProcessor]:
        return super().__call__(obj)
