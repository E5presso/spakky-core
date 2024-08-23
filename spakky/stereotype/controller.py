from dataclasses import dataclass

from spakky.pod.pod import Pod


@dataclass
class Controller(Pod):
    prefix: str
