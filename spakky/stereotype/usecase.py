from dataclasses import dataclass

from spakky.pod.pod import Pod


@dataclass(eq=False)
class UseCase(Pod): ...
