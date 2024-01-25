from dataclasses import dataclass

from spakky.dependency.component import Component


@dataclass
class Controller(Component):
    prefix: str
