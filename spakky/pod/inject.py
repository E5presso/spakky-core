from typing import overload

from spakky.core.types import ObjectT
from spakky.pod.interfaces.container import IContainer


@overload
def inject(context: IContainer, type_: type[ObjectT]) -> ObjectT: ...


@overload
def inject(context: IContainer, type_: type[ObjectT], name: str) -> ObjectT: ...


def inject(
    context: IContainer,
    type_: type[ObjectT],
    name: str | None = None,
) -> object | ObjectT:
    if name is not None:
        return context.get(type_=type_, name=name)
    return context.get(type_=type_)
