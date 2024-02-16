import inspect
from uuid import UUID, uuid4
from typing import Any, Callable, Awaitable, cast
from datetime import datetime
from dataclasses import dataclass

import pytest

from spakky.aop.advisor import Advisor, AsyncAdvisor, P, R


def test_advisor_is_callable() -> None:
    class DummyAspect(Advisor):
        ...

    @DummyAspect()
    def sample(name: str, age: int) -> str:
        return name + str(age)

    assert isinstance(sample, Callable)
    assert inspect.isfunction(sample)


def test_advisor_type_attribute() -> None:
    class DummyAspect(Advisor):
        ...

    @DummyAspect()
    def func(name: str, age: int) -> tuple[str, int]:
        """dummy doc"""
        return name, age

    assert func.__module__ == "tests.spakky.unit.aop.test_advisor"
    assert func.__name__ == "func"
    assert func.__qualname__ == "test_advisor_type_attribute.<locals>.func"
    assert func.__doc__ == "dummy doc"
    assert func.__annotations__ == {"name": str, "age": int, "return": tuple[str, int]}


def test_advisor_before_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_called: bool = False

    class BeforeAspect(Advisor):
        def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal advisor_called
            advisor_called = True
            return super().before(*_args, **_kwargs)

    @BeforeAspect()
    def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert func(name="John", age=30) == User("John", 30)
    assert advisor_called is True


def test_advisor_after_returning_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterReturningAspect(Advisor):
        def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterReturningAspect()
    def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    user: User = func("John", 30)
    assert user.name == "John"
    assert user.age == 30
    assert advisor_returned is True
    assert advisor_raised is False
    assert return_value is not None
    assert return_value == user


def test_advisor_after_raising_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterRaisingAspect(Advisor):
        def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterRaisingAspect()
    def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        func("John", 30)
    assert advisor_returned is False
    assert advisor_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


def test_advisor_after_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterAspect(Advisor):
        def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return super().after_returning(_result)

        def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return super().after_raising(_error)

    @AfterAspect()
    def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        func(name="John", age=30)
    assert advisor_returned is False
    assert advisor_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


def test_advisor_around_expect_success() -> None:
    class AroundAspect(Advisor):
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


def test_log_advisor() -> None:
    logs: list[str] = []

    class LogAspect(Advisor):
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
async def test_async_advisor_is_coroutine_callable() -> None:
    class DummyAspect(AsyncAdvisor):
        ...

    @DummyAspect()
    async def sample(name: str, age: int) -> str:
        return name + str(age)

    assert isinstance(sample, Callable)
    assert inspect.isfunction(sample)
    assert inspect.iscoroutinefunction(sample)


@pytest.mark.asyncio
async def test_async_advisor_type_attribute() -> None:
    class DummyAspect(AsyncAdvisor):
        ...

    @DummyAspect()
    async def func(name: str, age: int) -> tuple[str, int]:
        """dummy doc"""
        return name, age

    assert func.__module__ == "tests.spakky.unit.aop.test_advisor"
    assert func.__name__ == "func"
    assert func.__qualname__ == "test_async_advisor_type_attribute.<locals>.func"
    assert func.__doc__ == "dummy doc"
    assert func.__annotations__ == {"name": str, "age": int, "return": tuple[str, int]}


@pytest.mark.asyncio
async def test_async_advisor_before_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_called: bool = False

    class BeforeAspect(AsyncAdvisor):
        async def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal advisor_called
            advisor_called = True
            return await super().before(*_args, **_kwargs)

    @BeforeAspect()
    async def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert await func(name="John", age=30) == User("John", 30)
    assert advisor_called is True


@pytest.mark.asyncio
async def test_async_advisor_after_returning_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterReturningAspect(AsyncAdvisor):
        async def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterReturningAspect()
    async def func(name: str, age: int) -> User:
        return User(name=name, age=age)

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    user: User = await func("John", 30)
    assert user.name == "John"
    assert user.age == 30
    assert advisor_returned is True
    assert advisor_raised is False
    assert return_value is not None
    assert return_value == user


@pytest.mark.asyncio
async def test_async_advisor_after_raising_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterRaisingAspect(AsyncAdvisor):
        async def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterRaisingAspect()
    async def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        await func("John", 30)
    assert advisor_returned is False
    assert advisor_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


@pytest.mark.asyncio
async def test_async_advisor_after_expect_success() -> None:
    @dataclass
    class User:
        name: str
        age: int

    advisor_returned: bool = False
    advisor_raised: bool = False
    return_value: User | None = None
    raised_exception: Exception | None = None

    class AfterAspect(AsyncAdvisor):
        async def after_returning(self, _result: Any) -> None:
            nonlocal advisor_returned
            nonlocal return_value
            advisor_returned = True
            return_value = cast(User, _result)
            return await super().after_returning(_result)

        async def after_raising(self, _error: Exception) -> None:
            nonlocal advisor_raised
            nonlocal raised_exception
            advisor_raised = True
            raised_exception = _error
            return await super().after_raising(_error)

    @AfterAspect()
    async def func(name: str, age: int) -> User:
        raise RuntimeError("Unexpected Runtime error occurred")

    assert advisor_returned is False
    assert advisor_raised is False
    assert return_value is None
    assert raised_exception is None
    with pytest.raises(RuntimeError):
        await func(name="John", age=30)
    assert advisor_returned is False
    assert advisor_raised is True
    assert return_value is None
    assert raised_exception is not None
    assert isinstance(raised_exception, RuntimeError)


@pytest.mark.asyncio
async def test_async_advisor_around_expect_success() -> None:
    class AroundAspect(AsyncAdvisor):
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
async def test_async_log_advisor() -> None:
    logs: list[str] = []

    class AsyncLogAspect(AsyncAdvisor):
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
