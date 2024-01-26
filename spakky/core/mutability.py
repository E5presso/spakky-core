from typing import dataclass_transform
from dataclasses import field, dataclass

from spakky.core.generics import ObjectT


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=False,
    field_specifiers=(field,),
)
def mutable(cls: type[ObjectT]) -> type[ObjectT]:
    return dataclass(frozen=False, kw_only=True, eq=False)(cls)


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=True,
    field_specifiers=(field,),
)
def immutable(cls: type[ObjectT]) -> type[ObjectT]:
    return dataclass(frozen=True, kw_only=True, eq=False)(cls)
