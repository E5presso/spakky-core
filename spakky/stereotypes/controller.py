from dataclasses import dataclass

from spakky.component.component import Component


@dataclass
class Controller(Component):
    prefix: str