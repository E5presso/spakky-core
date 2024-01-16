import inspect
from uuid import UUID, uuid4
from typing import Any, Callable, Awaitable, cast
from datetime import datetime
from dataclasses import dataclass

import pytest

from spakky.core.aspect import Aspect, AsyncAspect, P, R


def test_aspect_is_callable() -> None:
    class DummyAspect(Aspect):
        ...

    @DummyAspect()
    def sample(name: str, age: int) -> str:
        return name + str(age)

    assert isinstance(sample, Callable)
    assert inspect.isfunction(sample)


def test_aspect_type_attribute() -> None:
    class DummyAspect(Aspect):
        ...

    @DummyAspect()
    def func(name: str, age: int) -> tuple[str, int]:
        """dummy doc"""
        return name, age

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

    class BeforeAspect(Aspect):
        def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal aspect_called
            aspect_called = True
            return super().before(*_args, **_kwargs)

    @BeforeAspect()
    def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert func(name="John", age=30) == User("John", 30)
    assert aspect_called is True


def test_aspect_after_returning_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterReturningAspect(Aspect):
        def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterReturningAspect()
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

    class AfterRaisingAspect(Aspect):
        def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterRaisingAspect()
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

    class AfterAspect(Aspect):
        def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterAspect()
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
    with pytest.raises(AssertionError):
        func("John", 30)
    with pytest.raises(AssertionError):
        func(name="John", age=29)


def test_log_aspect() -> None:
    logs: list[str] = []

    class LogAspect(Aspect):
        request_id: UUID | None
        timestamp: datetime | None
        arguments: tuple[Any, ...] | None
        keywords: dict[str, Any] | None

        def __init__(self) -> None:
            self.request_id = None
            self.timestamp = None
            self.arguments = None
            self.keywords = None

        def before(self, *_args: Any, **_kwargs: Any) -> None:
            self.request_id = _kwargs.get("request_id", None)
            self.timestamp = datetime.now()
            self.arguments = _args
            self.keywords = _kwargs
            return super().before(*_args, **_kwargs)

        def after(self) -> None:
            nonlocal logs
            logs.append(
                f"[{self.request_id}][{self.timestamp}] {self.arguments}, {self.keywords}"
            )
            return super().after()

    @LogAspect()
    def execute(request_id: UUID, name: str, age: int) -> tuple[UUID, str, int]:
        return request_id, name, age

    uid1: UUID = uuid4()
    assert execute(request_id=uid1, name="John", age=30) == (uid1, "John", 30)
    uid2: UUID = uuid4()
    assert execute(request_id=uid2, name="John", age=30) == (uid2, "John", 30)
    uid3: UUID = uuid4()
    assert execute(request_id=uid3, name="John", age=30) == (uid3, "John", 30)
    uid4: UUID = uuid4()
    assert execute(request_id=uid4, name="John", age=30) == (uid4, "John", 30)

    assert len(logs) == 4


@pytest.mark.asyncio
async def test_async_aspect_is_coroutine_callable() -> None:
    class DummyAspect(AsyncAspect):
        ...

    @DummyAspect()
    async def sample(name: str, age: int) -> str:
        return name + str(age)

    assert isinstance(sample, Callable)
    assert inspect.isfunction(sample)
    assert inspect.iscoroutinefunction(sample)


@pytest.mark.asyncio
async def test_async_aspect_type_attribute() -> None:
    class DummyAspect(AsyncAspect):
        ...

    @DummyAspect()
    async def func(name: str, age: int) -> tuple[str, int]:
        """dummy doc"""
        return name, age

    assert func.__module__ == "tests.unit.core.test_aspect"
    assert func.__name__ == "func"
    assert func.__qualname__ == "test_async_aspect_type_attribute.<locals>.func"
    assert func.__doc__ == "dummy doc"
    assert func.__annotations__ == {"name": str, "age": int, "return": tuple[str, int]}


@pytest.mark.asyncio
async def test_async_aspect_before_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_called: bool = False

    class BeforeAspect(AsyncAspect):
        async def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal aspect_called
            aspect_called = True
            return await super().before(*_args, **_kwargs)

    @BeforeAspect()
    async def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert await func(name="John", age=30) == User("John", 30)
    assert aspect_called is True


@pytest.mark.asyncio
async def test_async_aspect_after_returning_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterReturningAspect(AsyncAspect):
        async def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterReturningAspect()
    async def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    user: User = await func("John", 30)
    assert user.name == "John"
    assert user.age == 30
    assert aspect_returned is True
    assert aspect_raised is False
    assert return_value is not None
    assert return_value == user


@pytest.mark.asyncio
async def test_async_aspect_after_raising_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterRaisingAspect(AsyncAspect):
        async def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterRaisingAspect()
    async def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        await func("John", 30)
    assert aspect_returned is False
    assert aspect_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


@pytest.mark.asyncio
async def test_async_aspect_after_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    aspect_returned: bool = False
    aspect_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterAspect(AsyncAspect):
        async def after_returning(self, _result: Any) -> None:
            nonlocal aspect_returned
            nonlocal return_value
            aspect_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal aspect_raised
            nonlocal raised_exception
            aspect_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterAspect()
    async def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert aspect_returned is False
    assert aspect_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        await func(name="John", age=30)
    assert aspect_returned is False
    assert aspect_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


@pytest.mark.asyncio
async def test_async_aspect_around_expect_success() -> None:
    class AroundAspect(AsyncAspect):
        async def around(
            self, func: Callable[P, Awaitable[R]], *args: P.args, **kwargs: P.kwargs
        ) -> R:
            assert not args
            assert kwargs == {"name": "John", "age": 30}
            result: R = await func(*args, **kwargs)
            assert result == "John30"
            return result

    @AroundAspect()
    async def func(name: str, age: int) -> str:
        return name + str(age)

    assert await func(name="John", age=30) == "John30"
    with pytest.raises(AssertionError):
        await func("John", 30)
    with pytest.raises(AssertionError):
        await func(name="John", age=29)


@pytest.mark.asyncio
async def test_async_log_aspect() -> None:
    logs: list[str] = []

    class AsyncLogAspect(AsyncAspect):
        request_id: UUID | None
        timestamp: datetime | None
        arguments: tuple[Any, ...] | None
        keywords: dict[str, Any] | None

        def __init__(self) -> None:
            self.request_id = None
            self.timestamp = None
            self.arguments = None
            self.keywords = None

        async def before(self, *_args: Any, **_kwargs: Any) -> None:
            self.request_id = _kwargs.get("request_id", None)
            self.timestamp = datetime.now()
            self.arguments = _args
            self.keywords = _kwargs
            return await super().before(*_args, **_kwargs)

        async def after(self) -> None:
            nonlocal logs
            logs.append(
                f"[{self.request_id}][{self.timestamp}] {self.arguments}, {self.keywords}"
            )
            return await super().after()

    @AsyncLogAspect()
    async def execute(request_id: UUID, name: str, age: int) -> tuple[UUID, str, int]:
        return request_id, name, age

    uid1: UUID = uuid4()
    assert await execute(request_id=uid1, name="John", age=30) == (uid1, "John", 30)
    uid2: UUID = uuid4()
    assert await execute(request_id=uid2, name="John", age=30) == (uid2, "John", 30)
    uid3: UUID = uuid4()
    assert await execute(request_id=uid3, name="John", age=30) == (uid3, "John", 30)
    uid4: UUID = uuid4()
    assert await execute(request_id=uid4, name="John", age=30) == (uid4, "John", 30)

    assert len(logs) == 4
