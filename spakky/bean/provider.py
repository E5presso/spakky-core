from enum import Enum, auto
from dataclasses import field, dataclass

from spakky.core.annotation import Annotation


class ProvidingType(Enum):
    SINGLETON = auto()
    FACTORY = auto()


@dataclass
class Provider(Annotation):
    providing_type: ProvidingType = field(default=ProvidingType.SINGLETON)
