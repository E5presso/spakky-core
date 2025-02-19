from dataclasses import dataclass

from spakky.pod.annotations.pod import Pod


@dataclass(eq=False)
class UseCase(Pod): ...
