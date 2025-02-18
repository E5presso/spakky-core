from typing import overload

from spakky.core.types import ObjectT
from spakky.pod.interfaces.container import IContainer


@overload
def inject(context: IContainer, *, name: str) -> object: ...


@overload
def inject(context: IContainer, *, type_: type[ObjectT]) -> ObjectT: ...


@overload
def inject(context: IContainer, *, name: str, type_: type[ObjectT]) -> ObjectT: ...


def inject(
    context: IContainer,
    type_: type[ObjectT] | None = None,
    name: str | None = None,
) -> object | ObjectT:
    if name is not None and type_ is not None:
        return context.get(name=name, type_=type_)
    if name is not None:
        return context.get(name=name)
    if type_ is not None:
        return context.get(type_=type_)
    raise ValueError("Either name or type_ must be provided")
