from spakky.application.interfaces.container import IPodContainer
from spakky.core.types import AnyT


def inject(context: IPodContainer, type_: type[AnyT], name: str | None = None) -> AnyT:
    return context.get(type_, name)
