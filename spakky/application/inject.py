from spakky.application.interfaces.container import IContainer
from spakky.core.types import AnyT


def inject(context: IContainer, type_: type[AnyT], name: str | None = None) -> AnyT:
    return context.get(type_, name)
