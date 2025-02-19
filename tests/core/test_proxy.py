from time import perf_counter_ns
from typing import Any

import pytest

from spakky.core.proxy import ProxyFactory, ProxyHandler
from spakky.core.types import AsyncFunc, Func


@pytest.mark.asyncio
async def test_proxy() -> None:
    get_count: int = 0
    set_count: int = 0
    deleted: set[str] = set()

    class Subject:
        name: str = "John"

        def call(self) -> str:
            return "Hello World!"

        async def call_async(self) -> str:
            return "Hello Async!"

    class MyMethodInterceptor(ProxyHandler):
        def call(self, method: Func, *args: Any, **kwargs: Any) -> Any:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: Any = super().call(method, *args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}ns")
            return result

        async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: Any = await super().call_async(method, *args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}ns")
            return result

        def get(self, name: str, value: Any) -> Any:
            nonlocal get_count
            get_count += 1
            return super().get(name, value)

        def set(self, name: str, value: Any) -> Any:
            nonlocal set_count
            set_count += 1
            return super().set(name, value)

        def delete(self, name: str, value: Any) -> Any:
            nonlocal deleted
            deleted.add(name)
            return super().delete(name, value)

    proxy: Subject = ProxyFactory(Subject, Subject(), MyMethodInterceptor()).create()
    assert proxy.call() == "Hello World!"
    assert await proxy.call_async() == "Hello Async!"
    assert proxy.name == "John"
    assert dir(proxy) == dir(Subject())

    with pytest.raises(AttributeError):
        del proxy.name

    assert get_count == 1
    assert set_count == 0
    assert deleted == {"name"}


@pytest.mark.asyncio
async def test_proxy_with_parameter() -> None:
    get_count: int = 0
    set_count: int = 0
    deleted: set[str] = set()

    class Subject:
        name: str

        def __init__(self, name: str) -> None:
            self.name = name

        def call(self) -> str:
            return f"Hello {self.name}!"

        async def call_async(self) -> str:
            return f"Hello {self.name}!"

    class MyMethodInterceptor(ProxyHandler):
        def call(self, method: Func, *args: Any, **kwargs: Any) -> Any:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: Any = super().call(method, *args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}ns")
            return result

        async def call_async(self, method: AsyncFunc, *args: Any, **kwargs: Any) -> Any:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: Any = await super().call_async(method, *args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}ns")
            return result

        def get(self, name: str, value: Any) -> Any:
            nonlocal get_count
            get_count += 1
            return super().get(name, value)

        def set(self, name: str, value: Any) -> Any:
            nonlocal set_count
            set_count += 1
            return super().set(name, value)

        def delete(self, name: str, value: Any) -> Any:
            nonlocal deleted
            deleted.add(name)
            return super().delete(name, value)

    proxy: Subject = ProxyFactory(
        Subject, Subject(name="John"), MyMethodInterceptor()
    ).create()
    assert proxy.call() == "Hello John!"
    assert await proxy.call_async() == "Hello John!"
    assert proxy.name == "John"
    assert dir(proxy) == dir(Subject("John"))

    del proxy.name

    assert get_count == 1
    assert set_count == 0
    assert deleted == {"name"}
