# type: ignore
# pylint: disable=wildcard-import, unused-import, unused-wildcard-import, no-name-in-module, possibly-used-before-assignment

import sys
from typing import *

if sys.version >= (3, 11):
    from typing import _collect_parameters  # pragma: no cover
else:
    from typing import _collect_type_vars  # pragma: no cover

__orig_bases__ = "__orig_bases__"
__parameters__ = "__parameters__"


def _generic_mro(result: dict[type, Any], tp: Any) -> None:
    origin = get_origin(tp)
    if origin is None:
        origin = tp
    result[origin] = tp
    if hasattr(origin, __orig_bases__):
        parameters = _collect_type_vars(getattr(origin, __orig_bases__))
        substitution = dict(zip(parameters, get_args(tp)))
        for base in origin.__orig_bases__:
            if get_origin(base) in result:
                continue
            base_parameters = getattr(base, __parameters__, ())
            if base_parameters:
                base = base[tuple(substitution.get(p, p) for p in base_parameters)]
            _generic_mro(result, base)


def generic_mro(tp: Any) -> list[type]:
    origin = get_origin(tp)
    if origin is None and not hasattr(tp, __orig_bases__):
        if not isinstance(tp, type):
            raise TypeError(f"{tp!r} is not a type or a generic alias")
        return tp.mro()
    # sentinel value to avoid to subscript Generic and Protocol
    result = {Generic: Generic, Protocol: Protocol}
    _generic_mro(result, tp)
    cls = origin if origin is not None else tp
    return list(result.get(sub_cls, sub_cls) for sub_cls in cls.__mro__)
