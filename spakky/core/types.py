from typing import Any, TypeVar, Callable, Awaitable, ParamSpec, TypeAlias, TypeGuard
from inspect import iscoroutinefunction

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

ClassT = TypeVar("ClassT", bound=type)
ClassT_co = TypeVar("ClassT_co", bound=type, covariant=True)
ClassT_contra = TypeVar("ClassT_contra", bound=type, contravariant=True)

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


def is_function(obj: Any) -> TypeGuard[Func | AsyncFunc]:
    return callable(obj)


def is_async_function(obj: Any) -> TypeGuard[AsyncFunc]:
    return callable(obj) and iscoroutinefunction(obj)
