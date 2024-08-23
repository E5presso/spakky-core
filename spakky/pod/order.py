from dataclasses import dataclass

from spakky.core.annotation import ClassAnnotation


@dataclass
class Order(ClassAnnotation):
    order: int

    def __post_init__(self) -> None:
        if self.order < 0:
            raise ValueError("Order cannot be negative")
