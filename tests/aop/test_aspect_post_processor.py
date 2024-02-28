import logging
from typing import Any
from dataclasses import dataclass

import pytest

from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.pointcut import (
    After,
    AfterRaising,
    AfterReturning,
    Around,
    AsyncAfter,
    AsyncAfterRaising,
    AsyncAfterReturning,
    AsyncAround,
    AsyncBefore,
    Before,
)
from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import Bean
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, AsyncFuncT, Func


def test_aspect_post_processor() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvice:
        @Before(Log.contains)
        def before(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AfterReturning(Log.contains)
        def after_returning(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @After(Log.contains)
        def after(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @Around(Log.contains)
        def around(
            self,
            joinpoint: Func,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            nonlocal logs
            try:
                result = joinpoint(*args, **kwargs)
            except Exception as e:
                logs.append(f"around {args}, {kwargs} {e}")
                raise
            else:
                logs.append(f"around {args}, {kwargs} {result}")
                return result

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvice)

    context.start()

    service: EchoService = context.get(required_type=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


def test_aspect_post_processor_raise_error() -> None:
    logs: list[str] = []

    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvice:
        @Before(Log.contains)
        def before(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AfterReturning(Log.contains)
        def after_returning(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @After(Log.contains)
        def after(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @Around(Log.contains)
        def around(
            self,
            joinpoint: Func,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            nonlocal logs
            try:
                result = joinpoint(*args, **kwargs)
            except Exception as e:
                logs.append(f"around {args}, {kwargs} {e}")
                raise
            else:
                logs.append(f"around {args}, {kwargs} {result}")
                return result

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvice)

    context.start()

    service: EchoService = context.get(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} "
    assert logs[2] == "after_raising "
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aspect_post_processor() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvice:
        @AsyncBefore(AsyncLog.contains)
        async def before(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AsyncAfterRaising(AsyncLog.contains)
        async def after_raising(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AsyncAfterReturning(AsyncLog.contains)
        async def after_returning(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @AsyncAfter(AsyncLog.contains)
        async def after(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @AsyncAround(AsyncLog.contains)
        async def around(
            self,
            joinpoint: AsyncFunc,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            nonlocal logs
            try:
                result = await joinpoint(*args, **kwargs)
            except Exception as e:
                logs.append(f"around {args}, {kwargs} {e}")
                raise
            else:
                logs.append(f"around {args}, {kwargs} {result}")
                return result

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvice)

    context.start()

    service: EchoService = context.get(required_type=EchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aspect_post_processor_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvice:
        @AsyncBefore(AsyncLog.contains)
        async def before(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AsyncAfterRaising(AsyncLog.contains)
        async def after_raising(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AsyncAfterReturning(AsyncLog.contains)
        async def after_returning(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @AsyncAfter(AsyncLog.contains)
        async def after(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @AsyncAround(AsyncLog.contains)
        async def around(
            self,
            joinpoint: AsyncFunc,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            nonlocal logs
            try:
                result = await joinpoint(*args, **kwargs)
            except Exception as e:
                logs.append(f"around {args}, {kwargs} {e}")
                raise
            else:
                logs.append(f"around {args}, {kwargs} {result}")
                return result

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvice)

    context.start()

    service: EchoService = context.get(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} "
    assert logs[2] == "after_raising "
    assert logs[3] == "after"