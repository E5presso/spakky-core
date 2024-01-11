from typing import Any, TypeVar, Callable

ObjectT = TypeVar("ObjectT", bound=Any)
ClassT = TypeVar("ClassT", bound=type)
ActionT = TypeVar("ActionT", bound=Callable[..., None])
FuncT = TypeVar("FuncT", bound=Callable[..., Any])
