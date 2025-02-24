# 이 코드는 https://github.com/python/typing/issues/777 에서 제안된 코드를 기반으로 작성되었습니다.
# type: ignore

import sys
from typing import *  # noqa: F403
from typing import Any, Generic, Protocol, TypeGuard, get_args, get_origin

from spakky.core.constants import ORIGIN_BASES, PARAMETERS
from spakky.core.types import ClassT

if sys.version_info >= (3, 11):
    from typing import _collect_parameters  # pragma: no cover
else:
    from typing import _collect_type_vars  # pragma: no cover


def _generic_mro(result: dict[type, Any], tp: Any) -> None:
    origin = get_origin(tp)
    if origin is None:
        origin = tp
    result[origin] = tp
    if hasattr(origin, ORIGIN_BASES):
        if sys.version_info >= (3, 11):
            parameters = _collect_parameters(
                getattr(origin, ORIGIN_BASES)
            )  # pragma: no cover
        else:
            parameters = _collect_type_vars(
                getattr(origin, ORIGIN_BASES)
            )  # pragma: no cover
        substitution = dict(zip(parameters, get_args(tp)))
        for base in origin.__orig_bases__:
            if get_origin(base) in result:
                continue
            base_parameters = getattr(base, PARAMETERS, ())
            if base_parameters:
                base = base[tuple(substitution.get(p, p) for p in base_parameters)]
            _generic_mro(result, base)


def generic_mro(tp: Any) -> list[type]:
    origin = get_origin(tp)
    if origin is None and not hasattr(tp, ORIGIN_BASES):
        if not isinstance(tp, type):
            raise TypeError(f"{tp!r} is not a type or a generic alias")
        return tp.mro()
    # sentinel value to avoid to subscript Generic and Protocol
    result = {Generic: Generic, Protocol: Protocol}
    _generic_mro(result, tp)
    cls = origin if origin is not None else tp
    return list(result.get(sub_cls, sub_cls) for sub_cls in cls.__mro__)
    cls = origin if origin is not None else tp
    return list(result.get(sub_cls, sub_cls) for sub_cls in cls.__mro__)


def is_family_with(tp: Any, target: ClassT) -> TypeGuard[ClassT]:
    return target in generic_mro(tp)
