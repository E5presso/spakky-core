from dataclasses import dataclass

from spakky.bean.bean import Bean


@dataclass
class Controller(Bean):
    prefix: str
