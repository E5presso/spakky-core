from typing import Any, TypeVar, Callable, Awaitable, ParamSpec, TypeAlias

Func: TypeAlias = Callable[..., Any]
AsyncFunc: TypeAlias = Callable[..., Awaitable[Any]]
Action: TypeAlias = Callable[..., None]
AsyncAction: TypeAlias = Callable[..., Awaitable[None]]

AnyT = TypeVar("AnyT", bound=Any)
ObjectT = TypeVar("ObjectT", bound=object)
ClassT = TypeVar("ClassT", bound=type)
FuncT = TypeVar("FuncT", bound=Func)
AsyncFuncT = TypeVar("AsyncFuncT", bound=AsyncFunc)
ActionT = TypeVar("ActionT", bound=Action)
AsyncActionT = TypeVar("AsyncActionT", bound=AsyncAction)

P = ParamSpec("P")
R = TypeVar("R")
