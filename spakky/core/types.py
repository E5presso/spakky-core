from types import UnionType
from typing import (
    Any,
    Union,
    TypeVar,
    Callable,
    Optional,
    Awaitable,
    ParamSpec,
    TypeAlias,
    TypeGuard,
    get_args,
    get_origin,
)

Class: TypeAlias = type[Any]
Func: TypeAlias = Callable[..., Any]
AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]
Action: TypeAlias = Callable[..., None]
AsyncAction: TypeAlias = Callable[..., Awaitable[None]]

AnyT = TypeVar("AnyT", bound=Any)
AnyT_co = TypeVar("AnyT_co", bound=Any, covariant=True)
AnyT_contra = TypeVar("AnyT_contra", bound=Any, contravariant=True)

ObjectT = TypeVar("ObjectT", bound=object)
ObjectT_co = TypeVar("ObjectT_co", bound=object, covariant=True)
ObjectT_contra = TypeVar("ObjectT_contra", bound=object, contravariant=True)

ClassT = TypeVar("ClassT", bound=Class)
ClassT_co = TypeVar("ClassT_co", bound=Class, covariant=True)
ClassT_contra = TypeVar("ClassT_contra", bound=Class, contravariant=True)

FuncT = TypeVar("FuncT", bound=Func)
FuncT_co = TypeVar("FuncT_co", bound=Func, covariant=True)
FuncT_contra = TypeVar("FuncT_contra", bound=Func, contravariant=True)

AsyncFuncT = TypeVar("AsyncFuncT", bound=AsyncFunc)
AsyncFuncT_co = TypeVar("AsyncFuncT_co", bound=AsyncFunc, covariant=True)
AsyncFuncT_contra = TypeVar("AsyncFuncT_contra", bound=AsyncFunc, contravariant=True)

ActionT = TypeVar("ActionT", bound=Action)
ActionT_co = TypeVar("ActionT_co", bound=Action, covariant=True)
ActionT_contra = TypeVar("ActionT_contra", bound=Action, contravariant=True)

AsyncActionT = TypeVar("AsyncActionT", bound=AsyncAction)
AsyncActionT_co = TypeVar("AsyncActionT_co", bound=AsyncAction, covariant=True)
AsyncActionT_contra = TypeVar(
    "AsyncActionT_contra", bound=AsyncAction, contravariant=True
)

P = ParamSpec("P")
R = TypeVar("R")


def is_optional(type_: Any) -> TypeGuard[Optional[Any]]:
    origin_type: type = get_origin(type_)
    is_union_type: bool = origin_type is UnionType or origin_type is Union
    includes_none = type(None) in get_args(type_)
    is_union_with_none: bool = is_union_type and includes_none
    return is_union_with_none
