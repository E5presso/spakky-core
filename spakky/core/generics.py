from typing import Any, TypeVar, Callable, TypeAlias

Func: TypeAlias = Callable[..., Any]
Action: TypeAlias = Callable[..., None]

AnyT = TypeVar("AnyT", bound=Any)
ObjectT = TypeVar("ObjectT", bound=object)
ClassT = TypeVar("ClassT", bound=type)
FuncT = TypeVar("FuncT", bound=Callable[..., Any])
ActionT = TypeVar("ActionT", bound=Callable[..., None])
