import logging
from typing import Any
from dataclasses import dataclass

import pytest

from spakky.aop.advice import After, AfterRaising, AfterReturning, Around, Before
from spakky.aop.advisor import IAdvisor, IAsyncAdvisor
from spakky.aop.aspect import Aspect, AsyncAspect
from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean, BeanFactory
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, AsyncFuncT, Func


def test_aop_with_no_implementations() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
        @Before(Log.contains)
        def before(self, *args: Any, **kwargs: Any) -> None:
            return super().before(*args, **kwargs)

        @AfterReturning(Log.contains)
        def after_returning(self, result: Any) -> None:
            return super().after_returning(result)

        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            return super().after_raising(error)

        @After(Log.contains)
        def after(self) -> None:
            return super().after()

        @Around(Log.contains)
        def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
            return super().around(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
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
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


def test_aop_with_another_bean() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
        @Before(Log.contains)
        def before(self, *args: Any, **kwargs: Any) -> None:
            return super().before(*args, **kwargs)

        @AfterReturning(Log.contains)
        def after_returning(self, result: Any) -> None:
            return super().after_returning(result)

        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            return super().after_raising(error)

        @After(Log.contains)
        def after(self) -> None:
            return super().after()

        @Around(Log.contains)
        def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
            return super().around(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    @Bean()
    class AnotherService:
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AnotherService)
    context.register_bean(LogAdvisor)

    context.start()

    assert (
        context.single(required_type=EchoService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert (
        context.single(required_type=AnotherService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert len(logs) == 0


def test_aop_with_no_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
        @Before(Log.contains)
        def before(self, *args: Any, **kwargs: Any) -> None:
            return super().before(*args, **kwargs)

        @AfterReturning(Log.contains)
        def after_returning(self, result: Any) -> None:
            return super().after_returning(result)

        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            return super().after_raising(error)

        @After(Log.contains)
        def after(self) -> None:
            return super().after()

        @Around(Log.contains)
        def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
            return super().around(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop_raise_error() -> None:
    logs: list[str] = []

    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
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
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} "
    assert logs[2] == "after_raising "
    assert logs[3] == "after"


def test_aop_that_does_not_have_any_aspects() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
        def before(self, *args: Any, **kwargs: Any) -> None:
            return super().before(*args, **kwargs)

        def after_returning(self, result: Any) -> None:
            return super().after_returning(result)

        def after_raising(self, error: Exception) -> None:
            return super().after_raising(error)

        def after(self) -> None:
            return super().after()

        def around(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
            return super().around(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop_with_no_method() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
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
        message = "Hello World!"

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert service.message == "Hello World!"
    assert len(logs) == 0


def test_aop_with_dependencies() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation):
        ...

    @Aspect()
    class LogAdvisor(IAdvisor):
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
        message: str

        @autowired
        def __init__(self, message: str) -> None:
            self.message = message

        @Log()
        def echo(self) -> str:
            return self.message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    @BeanFactory(bean_name="message")
    def get_message() -> str:
        return "Hello World!"

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean_factory(get_message)
    context.register_bean(EchoService)
    context.register_bean(LogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert service.message == "Hello World!"
    assert service.echo() == "Hello World!"
    assert logs[0] == "before (), {}"
    assert logs[1] == "around (), {} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aop_with_no_implementations() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            return await super().before_async(*args, **kwargs)

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            return await super().after_raising_async(error)

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            return await super().after_returning_async(result)

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            return await super().after_async()

        @Around(AsyncLog.contains)
        async def around_async(
            self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any
        ) -> Any:
            return await super().around_async(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_async_aop() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @Around(AsyncLog.contains)
        async def around_async(
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
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aop_with_another_bean() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            return await super().before_async(*args, **kwargs)

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            return await super().after_raising_async(error)

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            return await super().after_returning_async(result)

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            return await super().after_async()

        @Around(AsyncLog.contains)
        async def around_async(
            self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any
        ) -> Any:
            return await super().around_async(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    @Bean()
    class AnotherService:
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AnotherService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    assert (
        await context.single(required_type=EchoService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert (
        await context.single(required_type=AnotherService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_async_aop_with_no_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            return await super().before_async(*args, **kwargs)

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            return await super().after_raising_async(error)

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            return await super().after_returning_async(result)

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            return await super().after_async()

        @Around(AsyncLog.contains)
        async def around_async(
            self, joinpoint: AsyncFunc, *args: Any, **kwargs: Any
        ) -> Any:
            return await super().around_async(joinpoint, *args, **kwargs)

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert await service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_async_aop_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @Around(AsyncLog.contains)
        async def around_async(
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
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(EchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.single(required_type=EchoService)
    with pytest.raises(RuntimeError):
        assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} "
    assert logs[2] == "after_raising "
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aop_that_does_not_have_any_aspects() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            return await super().before_async(*args, **kwargs)

        async def after_returning_async(self, result: Any) -> None:
            return await super().after_returning_async(result)

        async def after_raising_async(self, error: Exception) -> None:
            return await super().after_raising_async(error)

        async def after_async(self) -> None:
            return await super().after_async()

        async def around_async(self, joinpoint: Func, *args: Any, **kwargs: Any) -> Any:
            return await super().around_async(joinpoint, *args, **kwargs)

    @Bean()
    class AsyncEchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(AsyncEchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: AsyncEchoService = context.single(required_type=AsyncEchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_async_aop_with_no_method() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAdvisor):
        @Before(AsyncLog.contains)
        async def before_async(self, *args: Any, **kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {args}, {kwargs}")

        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {error}")

        @AfterReturning(AsyncLog.contains)
        async def after_returning_async(self, result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {result}")

        @After(AsyncLog.contains)
        async def after_async(self) -> None:
            nonlocal logs
            logs.append(f"after")

        @Around(AsyncLog.contains)
        async def around_async(
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
    class AsyncEchoService:
        message = "Hello World!"

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_bean_post_processor(AspectBeanPostProcessor(logger))
    context.register_bean(AsyncEchoService)
    context.register_bean(AsyncLogAdvisor)

    context.start()

    service: AsyncEchoService = context.single(required_type=AsyncEchoService)
    assert service.message == "Hello World!"
    assert len(logs) == 0
