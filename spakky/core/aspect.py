from typing import Any, Generic, TypeVar, Callable, ParamSpec, final

P = ParamSpec("P")
R = TypeVar("R")


# pylint: disable=unused-argument
class Aspect(Generic[P, R]):
    __func: Callable[P, R]

    def __init__(self, func: Callable[P, R]) -> None:
        self.__func = func

    @final
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        args, kwargs = self.before(*args, **kwargs)
        try:
            result: Any = self.around(self.__func, *args, **kwargs)
            self.after_returning(result, *args, **kwargs)
            return result
        except Exception as e:
            self.after_raising(e, *args, **kwargs)
            raise e from e
        finally:
            self.after(*args, **kwargs)

    @final
    def __getattribute__(self, __name: str) -> Any:
        if __name in (
            "__module__",
            "__name__",
            "__qualname__",
            "__doc__",
            "__annotations__",
        ):
            return getattr(self.__func, __name)
        return super().__getattribute__(__name)

    def before(self, *args: Any, **kwargs: Any) -> tuple[Any, Any]:
        return args, kwargs

    def after_returning(self, result: Any, *args: Any, **kwargs: Any) -> Any:
        return result

    def after_raising(self, exception: Exception, *args: Any, **kwargs: Any) -> None:
        return

    def after(self, *args: Any, **kwargs: Any) -> None:
        return

    def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Any:
        return func(*args, **kwargs)
