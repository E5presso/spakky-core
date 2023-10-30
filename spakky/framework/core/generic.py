from typing import Any, Callable, TypeVar


T_CLASS = TypeVar("T_CLASS", bound=type)
T_FUNC = TypeVar("T_FUNC", bound=Callable[..., Any])
