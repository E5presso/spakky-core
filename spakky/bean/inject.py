from typing import overload

from spakky.bean.application_context import ApplicationContext
from spakky.core.generics import AnyT


@overload
def inject(context: ApplicationContext, *, required_type: type[AnyT]) -> AnyT:
    ...


@overload
def inject(context: ApplicationContext, *, name: str) -> object:
    ...


def inject(
    context: ApplicationContext,
    required_type: type[AnyT] | None = None,
    name: str | None = None,
) -> AnyT | object:
    if name is not None:
        return context.get(name=name)
    if required_type is None:  # pragma: no cover
        raise ValueError("'name' and 'required_type' both cannot be None")
    return context.get(required_type=required_type)
