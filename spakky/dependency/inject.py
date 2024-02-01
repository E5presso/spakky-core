from typing import overload

from spakky.core.generics import ObjectT
from spakky.dependency.context import Context


@overload
def inject(*, context: Context, required_type: type[ObjectT]) -> ObjectT:
    ...


@overload
def inject(*, context: Context, name: str) -> object:
    ...


def inject(
    context: Context,
    required_type: type[ObjectT] | None = None,
    name: str | None = None,
) -> ObjectT | object:
    if required_type is not None:
        return context.get(required_type=required_type)
    if name is None:  # pragma: no cover
        raise ValueError("'required_type' and 'name' both cannot be None")
    return context.get(name=name)
