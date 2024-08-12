# pylint: disable=too-many-lines

import logging
from typing import Any
from dataclasses import dataclass

import pytest

from spakky.aop.advice import After, AfterRaising, AfterReturning, Around, Before
from spakky.aop.aspect import Aspect, AsyncAspect, IAspect, IAsyncAspect
from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.application_context import ApplicationContext
from spakky.core.annotation import FunctionAnnotation
from spakky.core.types import AsyncFunc, AsyncFuncT, Func
from spakky.injectable.injectable import Injectable


def test_aop_with_no_implementations() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect): ...

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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
            logs.append("after")

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

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


def test_aop_with_another_injectable() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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

    @Injectable()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AnotherService)
    context.register_injectable(LogAdvisor)

    context.start()

    assert context.get(type_=EchoService).echo(message="Hello World!") == "Hello World!"
    assert (
        context.get(type_=AnotherService).echo(message="Hello World!") == "Hello World!"
    )
    assert len(logs) == 0

    assert dir(context.get(type_=EchoService)) == dir(EchoService())


def test_aop_with_no_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect): ...

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop_with_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
        @AfterRaising(Log.contains)
        def after_raising(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {type(error).__name__}")
            return super().after_raising(error)

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"

    assert logs[0] == "after_raising RuntimeError"


def test_aop_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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
            logs.append("after")

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

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    with pytest.raises(RuntimeError):
        assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} "
    assert logs[2] == "after_raising "
    assert logs[3] == "after"


def test_aop_that_does_not_have_any_aspects() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect): ...

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


def test_aop_with_no_method() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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
            logs.append("after")

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

    @Injectable()
    class EchoService:
        message = "Hello World!"

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert service.message == "Hello World!"
    assert len(logs) == 0


def test_aop_with_dependencies() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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
            logs.append("after")

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

    @Injectable()
    class EchoService:
        message: str

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

    @Injectable(name="message")
    def get_message() -> str:
        return "Hello World!"

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(get_message)
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert service.message == "Hello World!"
    assert service.echo() == "Hello World!"
    assert logs[0] == "before (), {}"
    assert logs[1] == "around (), {} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


def test_aop_with_dependencies_no_typing() -> None:
    logs: list[str] = []

    @dataclass
    class Log(FunctionAnnotation): ...

    @Aspect()
    class LogAdvisor(IAspect):
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
            logs.append("after")

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

    @Injectable()
    class EchoService:
        message: str

        def __init__(self, message) -> None:  # type: ignore
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

    @Injectable(name="message")
    def get_message() -> str:
        return "Hello World!"

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(get_message)
    context.register_injectable(EchoService)
    context.register_injectable(LogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
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
    class AsyncLogAdvisor(IAsyncAspect): ...

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
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
    class AsyncLogAdvisor(IAsyncAspect):
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
            logs.append("after")

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

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "before (), {'message': 'Hello World!'}"
    assert logs[1] == "around (), {'message': 'Hello World!'} Hello World!"
    assert logs[2] == "after_returning Hello World!"
    assert logs[3] == "after"


@pytest.mark.asyncio
async def test_async_aop_with_another_injectable() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAspect):
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

    @Injectable()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AnotherService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    assert (
        await context.get(type_=EchoService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert (
        await context.get(type_=AnotherService).echo(message="Hello World!")
        == "Hello World!"
    )
    assert len(logs) == 0

    assert dir(context.get(type_=EchoService)) == dir(EchoService())


@pytest.mark.asyncio
async def test_async_aop_with_no_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAspect): ...

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    with pytest.raises(RuntimeError):
        assert await service.echo(message="Hello World!") == "Hello World!"
    assert len(logs) == 0


@pytest.mark.asyncio
async def test_async_aop_with_implementations_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAspect):
        @AfterRaising(AsyncLog.contains)
        async def after_raising_async(self, error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {type(error).__name__}")
            return await super().after_raising_async(error)

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
    with pytest.raises(RuntimeError):
        assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "after_raising RuntimeError"


@pytest.mark.asyncio
async def test_async_aop_raise_error() -> None:
    logs: list[str] = []

    @dataclass
    class AsyncLog(FunctionAnnotation):
        def __call__(self, obj: AsyncFuncT) -> AsyncFuncT:
            return super().__call__(obj)

    @AsyncAspect()
    class AsyncLogAdvisor(IAsyncAspect):
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
            logs.append("after")

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

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(EchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: EchoService = context.get(type_=EchoService)
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
    class AsyncLogAdvisor(IAsyncAspect):
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

    @Injectable()
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

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(AsyncEchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: AsyncEchoService = context.get(type_=AsyncEchoService)
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
    class AsyncLogAdvisor(IAsyncAspect):
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
            logs.append("after")

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

    @Injectable()
    class AsyncEchoService:
        message = "Hello World!"

    context: ApplicationContext = ApplicationContext()

    console = logging.StreamHandler()
    console.setLevel(level=logging.DEBUG)
    console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
    logger: logging.Logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

    context.register_post_processor(AspectPostProcessor(logger))
    context.register_injectable(AsyncEchoService)
    context.register_injectable(AsyncLogAdvisor)

    context.start()

    service: AsyncEchoService = context.get(type_=AsyncEchoService)
    assert service.message == "Hello World!"
    assert len(logs) == 0
