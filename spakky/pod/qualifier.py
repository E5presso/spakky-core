from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

from spakky.core.metadata import Metadata

if TYPE_CHECKING:
    from spakky.pod.pod import Pod


@dataclass
class Qualifier(Metadata):
    selector: Callable[["Pod"], bool]
