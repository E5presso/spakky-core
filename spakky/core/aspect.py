from typing import Any, TypeVar, Callable, ParamSpec
from functools import wraps

from spakky.core.annotation import Annotation

P = ParamSpec("P")
R = TypeVar("R")


class Aspect(Annotation):
    """`Aspect` class is made to support Aspect Oriented Programming.\n
    You can override joinpoint such as\n
    [`before`, `after_returning`, `after_raising`, `after`, `around`]\n
    This is Proxy Wrapper for Callable object.\n
    Here is a example.\n
    ```python
    class AroundAspect(Aspect):
        def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
            assert not args
            assert kwargs == {"name": "John", "age": 30}
            result: R = func(*args, **kwargs)
            assert result == "John30"
            return result

    @AroundAspect()
    def func(name: str, age: int) -> str:
        return name + str(age)

    assert func(name="John", age=30) == "John30"
    ```
    """

    def __call__(self, obj: Callable[P, R]) -> Callable[P, R]:
        """Annotate origin function to a Aspect wrapper.

        Args:
            obj (Callable[P, R]): Origin function to wrapped by Aspect

        Returns:
            Callable[P, R]: Wrapped function
        """
        obj = super().__call__(obj)

        @wraps(obj)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self.before(*args, **kwargs)
            try:
                result: Any = self.around(obj, *args, **kwargs)
                self.after_returning(result)
                return result
            except Exception as e:
                self.after_raising(e)
                raise e from e
            finally:
                self.after()

        return wrapper

    def before(self, *_args: Any, **_kwargs: Any) -> None:
        return

    def after_returning(self, _result: Any) -> None:
        return

    def after_raising(self, _error: Exception) -> None:
        return

    def after(self) -> None:
        return

    def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)
