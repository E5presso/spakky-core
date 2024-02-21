from typing import Any, TypeVar, Callable, Awaitable, TypeAlias

Func: TypeAlias = Callable[..., Any]
Action: TypeAlias = Callable[..., None]

AnyT = TypeVar("AnyT", bound=Any)
ObjectT = TypeVar("ObjectT", bound=object)
ClassT = TypeVar("ClassT", bound=type)
FuncT = TypeVar("FuncT", bound=Callable[..., Any])
AsyncFuncT = TypeVar("AsyncFuncT", bound=Callable[..., Awaitable[Any]])
ActionT = TypeVar("ActionT", bound=Callable[..., None])
AsyncActionT = TypeVar("AsyncActionT", bound=Callable[..., Awaitable[None]])
