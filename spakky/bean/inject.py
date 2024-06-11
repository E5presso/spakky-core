from typing import overload

from spakky.bean.interfaces.bean_container import IBeanContainer
from spakky.core.types import AnyT


@overload
def inject(context: IBeanContainer, *, required_type: type[AnyT]) -> AnyT: ...


@overload
def inject(context: IBeanContainer, *, name: str) -> object: ...


def inject(
    context: IBeanContainer,
    required_type: type[AnyT] | None = None,
    name: str | None = None,
) -> AnyT | object:
    if name is not None:
        return context.single(name=name)
    if required_type is None:  # pragma: no cover
        raise ValueError("'name' and 'required_type' both cannot be None")
    return context.single(required_type=required_type)
