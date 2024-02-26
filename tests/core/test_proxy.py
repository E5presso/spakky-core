from time import perf_counter_ns
from typing import Callable

from spakky.core.proxy import Enhancer, IInvocationHandler, P, R


def test_proxy() -> None:
    class Subject:
        message: str

        def __init__(self, message: str) -> None:
            self.message = message

        def call(self) -> str:
            return self.message

    class MyInvocationHandler(IInvocationHandler):
        def intercept(
            self,
            target: object,
            method: Callable[P, R],
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            print("TimeProxy 실행")
            start_time = perf_counter_ns()
            result: R = method(*args, **kwargs)
            end_time = perf_counter_ns()
            result_time = end_time - start_time
            print(f"TimeProxy 종료 result_time = {result_time}")
            return result

    proxy: Subject = Enhancer(Subject, MyInvocationHandler()).create(
        message="Hello World!"
    )
    assert proxy.call() == "Hello World!"
