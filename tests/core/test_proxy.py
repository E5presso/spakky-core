from time import perf_counter_ns
from types import MethodType
from typing import Any

from spakky.core.proxy import Enhancer, IMethodInterceptor


def test_proxy() -> None:
    class Subject:
        name: str = "John"

        def call(self) -> str:
            return "Hello World!"

    class MyMethodInterceptor(IMethodInterceptor):
        def intercept(self, method: MethodType, *args: Any, **kwargs: Any) -> Any:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: Any = method(*args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}ns")
            return result

    proxy: Subject = Enhancer(Subject, MyMethodInterceptor()).create()
    assert proxy.call() == "Hello World!"
    assert proxy.name == "John"
