from abc import ABC
from dataclasses import dataclass
from typing import Annotated, cast, get_args

from spakky.core.types import ClassT


@dataclass
class Metadata(ABC): ...


def get_metadata(annotated: Annotated[ClassT, ...]) -> tuple[ClassT, list[Metadata]]:
    metadata = get_args(annotated)
    return cast(ClassT, metadata[0]), [
        data for data in metadata[1:] if isinstance(data, Metadata)
    ]
