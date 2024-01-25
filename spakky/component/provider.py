from enum import Enum, auto
from dataclasses import field, dataclass

from spakky.core.annotation import ClassAnnotation


class ProvidingType(Enum):
    SINGLETON = auto()
    FACTORY = auto()


@dataclass
class Provider(ClassAnnotation):
    providing_type: ProvidingType = field(default=ProvidingType.SINGLETON)
