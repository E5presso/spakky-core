from typing import Any, TypeVar, Callable

ObjectT = TypeVar("ObjectT", bound=Any)
ClassT = TypeVar("ClassT", bound=type)
FuncT = TypeVar("FuncT", bound=Callable[..., Any])
ActionT = TypeVar("ActionT", bound=Callable[..., None])
