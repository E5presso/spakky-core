import sys
from dataclasses import dataclass, field

from spakky.core.types import AnyT

if sys.version_info >= (3, 11):
    from typing import dataclass_transform  # pragma: no cover
else:
    from typing_extensions import dataclass_transform  # pragma: no cover


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=False,
    field_specifiers=(field,),
)
def mutable(cls: type[AnyT]) -> type[AnyT]:
    return dataclass(frozen=False, kw_only=True, eq=False)(cls)


@dataclass_transform(
    eq_default=False,
    kw_only_default=True,
    frozen_default=True,
    field_specifiers=(field,),
)
def immutable(cls: type[AnyT]) -> type[AnyT]:
    return dataclass(frozen=True, kw_only=True, eq=False)(cls)
