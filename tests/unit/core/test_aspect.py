from typing import Any, Generic, Callable
from dataclasses import dataclass

import pytest

from spakky.core.aspect import Aspect, P, R


def test_aspect_is_callable() -> None:
    class DummyAspect(Aspect[P, R], Generic[P, R]):
        ...

    assert isinstance(Aspect, Callable)
    assert isinstance(DummyAspect, Callable)


def test_aspect_type_attribute() -> None:
    class DummyAspect(Aspect[P, R], Generic[P, R]):
        ...

    @DummyAspect
    def func(name: str, age: int) -> tuple[str, int]:
        """dummy doc"""
        return name, age

    assert func(name="John", age=30) == ("John", 30)
    assert func.__module__ == "tests.unit.core.test_aspect"
    assert func.__name__ == "func"
    assert func.__qualname__ == "test_aspect_type_attribute.<locals>.func"
    assert func.__doc__ == "dummy doc"
    assert func.__annotations__ == {"name": str, "age": int, "return": tuple[str, int]}


def test_aspect_before_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_called: bool = False

    class BeforeAspect(Aspect[P, R], Generic[P, R]):
        def before(self, *args: Any, **kwargs: Any) -> tuple[Any, Any]:
            nonlocal aspect_called
            aspect_called = True
            return super().before(*args, **kwargs)

    @BeforeAspect
    def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert func(name="John", age=30) == User("John", 30)
    assert aspect_called is True


def test_aspect_before_mutate_arg() -> None:
    class BeforeAspect(Aspect[P, R], Generic[P, R]):
        def before(self, *args: Any, **kwargs: Any) -> tuple[Any, Any]:
            _, age = args
            return super().before("Sarah", age, **kwargs)

    @BeforeAspect
    def func(name: str, age: int) -> tuple[str, int]:
        return name, age

    assert func("John", 30) == ("Sarah", 30)


def test_aspect_after_returning_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterReturningAspect(Aspect[P, R], Generic[P, R]):
        def after_returning(self, result: User, *args: Any, **kwargs: Any) -> User:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = result
            return super().after_returning(result, *args, **kwargs)

        def after_raising(self, exception: Exception, *args: Any, **kwargs: Any) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = exception
            return super().after_raising(exception, *args, **kwargs)

    @AfterReturningAspect
    def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    user: User = func("John", 30)
    assert user.name == "John"
    assert user.age == 30
    assert aspect_returned is True
    assert aspect_raised is False
    assert return_value is not None
    assert return_value == user


def test_aspect_after_raising_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterRaisingAspect(Aspect[P, R], Generic[P, R]):
        def after_returning(self, result: Any, *args: Any, **kwargs: Any) -> Any:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = result
            return super().after_returning(result, *args, **kwargs)

        def after_raising(self, exception: Exception, *args: Any, **kwargs: Any) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = exception
            return super().after_raising(exception, *args, **kwargs)

    @AfterRaisingAspect
    def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        func("John", 30)
    assert aspect_returned is False
    assert aspect_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


def test_aspect_after_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterAspect(Aspect[P, R], Generic[P, R]):
        def after_returning(self, result: Any, *args: Any, **kwargs: Any) -> Any:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = result
            return super().after_returning(result, *args, **kwargs)

        def after_raising(self, exception: Exception, *args: Any, **kwargs: Any) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = exception
            return super().after_raising(exception, *args, **kwargs)

    @AfterAspect
    def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        func(name="John", age=30)
    assert aspect_returned is False
    assert aspect_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


def test_aspect_around_expect_success() -> None:
    class AroundAspect(Aspect[P, R], Generic[P, R]):
        def around(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Any:
            assert not args
            assert kwargs == {"name": "John", "age": 30}
            result: R = func(*args, **kwargs)
            assert result == "John30"
            return result

    @AroundAspect
    def func(name: str, age: int) -> str:
        return name + str(age)

    assert func(name="John", age=30) == "John30"
