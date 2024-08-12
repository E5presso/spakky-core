from dataclasses import dataclass

from spakky.injectable.injectable import Injectable


@dataclass
class Controller(Injectable):
    prefix: str
