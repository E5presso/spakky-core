from enum import Enum, auto
from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation


class ProvidingType(Enum):
    """This enumeration type is for providing components
    You can specify providing strategy between `SINGLETON` or `FACTORY`
    """

    SINGLETON = auto()
    FACTORY = auto()


@dataclass
class Provider(ClassAnnotation):
    """`Provider` annotation is for specifying loading strategy
    for Component\n
    You can specify providing component between `SINGLETON` or `FACTORY`\n
    Default value is `ProvidingType.SINGLETON`

    Example:
        ```python
        @Provider(ProvidingType.FACTORY)
        @Component
        class A:
            ...
        ```
    """

    providing_type: ProvidingType = field(default=ProvidingType.SINGLETON)
