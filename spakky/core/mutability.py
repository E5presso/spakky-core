from dataclasses import field, dataclass

from typing_extensions import dataclass_transform

from spakky.core.generics import AnyT


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=False,
    field_specifiers=(field,),
)
def mutable(cls: type[AnyT]) -> type[AnyT]:
    """Make class as mutable dataclass

    Args:
        cls (type[ObjectT]): Class to decorate as mutable dataclass

    Returns:
        type[ObjectT]: Decorated class
    """
    return dataclass(frozen=False, kw_only=True, eq=False)(cls)


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=True,
    field_specifiers=(field,),
)
def immutable(cls: type[AnyT]) -> type[AnyT]:
    """Make class as immutable(frozen) dataclass

    Args:
        cls (type[ObjectT]): Class to decorate as immutable(frozen) dataclass

    Returns:
        type[ObjectT]: Decorated class
    """
    return dataclass(frozen=True, kw_only=True, eq=False)(cls)
