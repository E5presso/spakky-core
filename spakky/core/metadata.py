from abc import ABC
from typing import Annotated, cast, get_args
from dataclasses import dataclass

from spakky.core.types import ClassT

__METADATA__ = "__metadata__"


@dataclass
class Metadata(ABC): ...


def get_metadata(annotated: Annotated[ClassT, ...]) -> tuple[ClassT, list[Metadata]]:
    metadata = get_args(annotated)
    return cast(ClassT, metadata[0]), [
        data for data in metadata[1:] if isinstance(data, Metadata)
    ]
