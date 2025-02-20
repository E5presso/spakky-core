from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from spakky.core.metadata import Metadata

if TYPE_CHECKING:
    from spakky.pod.annotations.pod import Pod


@dataclass
class Qualifier(Metadata):
    selector: Callable[["Pod"], bool]
