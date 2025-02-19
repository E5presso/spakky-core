import sys
from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation


@dataclass
class Order(ClassAnnotation):
    order: int = field(default=sys.maxsize)

    def __post_init__(self) -> None:
        if self.order < 0:
            raise ValueError("Order cannot be negative")
