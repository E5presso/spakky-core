from abc import ABC
from inspect import signature
from typing import Any, Callable, TypeAlias, final


AnyCallable: TypeAlias = Callable[..., Any]


class Aspect(ABC):
    @final
    def __call__(self, function: AnyCallable) -> AnyCallable:
        def wrapper(*args, **kwargs) -> Any:
            self.around()
            self.before()
            try:
                return_value: Any = function(*args, **kwargs)
            except Exception as e:
                self.after_exception()
                raise e from e
            else:
                self.after_return()
            finally:
                self.after()
                self.around()
            return return_value

        setattr(wrapper, "__signature__", signature(function))
        return wrapper

    def before(self) -> None:
        return

    def after(self) -> None:
        return

    def around(self) -> None:
        return

    def after_exception(self) -> None:
        return

    def after_return(self) -> None:
        return
