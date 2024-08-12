from typing import overload

from spakky.application.interfaces.container import IContainer
from spakky.core.types import AnyT


@overload
def inject(context: IContainer, *, type_: type[AnyT]) -> AnyT: ...


@overload
def inject(context: IContainer, *, name: str) -> object: ...


def inject(
    context: IContainer,
    type_: type[AnyT] | None = None,
    name: str | None = None,
) -> AnyT | object:
    if name is not None:
        return context.get(name=name)
    if type_ is not None:
        return context.get(type_=type_)
    raise ValueError("'name' and 'required_type' both cannot be None")  # pragma: no cover
