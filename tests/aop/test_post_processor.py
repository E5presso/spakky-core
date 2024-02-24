import logging
from typing import Any, Callable, Awaitable
from dataclasses import dataclass

import pytest

from spakky.aop.advice import (
    AbstractAdvice,
    AbstractAsyncAdvice,
    Aspect,
    AsyncPointcut,
    P,
    Pointcut,
    R,
)
from spakky.aop.post_processor import AspectDependencyPostPrecessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import Bean, BeanFactory


def test_aspect_post_processor() -> None:
    logs: list[str] = []

    @Aspect()
    class LogAdvice(AbstractAdvice):
        def before(self, _pointcut: Pointcut, *_args: Any, **_kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {_args}, {_kwargs}")
            return super().before(_pointcut, *_args, **_kwargs)

        def after_raising(self, _pointcut: Pointcut, _error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {_error}")
            return super().after_raising(_pointcut, _error)

        def after_returning(self, _pointcut: Pointcut, _result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {_result}")
            return super().after_returning(_pointcut, _result)

        def after(self, _pointcut: Pointcut) -> None:
            nonlocal logs
            logs.append(f"after")
            return super().after(_pointcut)

        def around(
            self,
            _pointcut: Pointcut,
            func: Callable[P, R],
            *_args: P.args,
            **_kwargs: P.kwargs,
        ) -> R:
            nonlocal logs
            try:
                result: R = super().around(_pointcut, func, *_args, **_kwargs)
            except Exception as e:
                logs.append(f"around {_args}, {_kwargs} {e}")
                raise
            else:
                logs.append(f"around {_args}, {_kwargs} {result}")
                return result

    @dataclass
    class Log(Pointcut):
        advice = LogAdvice

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    @BeanFactory()
    def logger() -> logging.Logger:
        console = logging.StreamHandler()
        console.setLevel(level=logging.DEBUG)
        console.setFormatter(
            logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s")
        )
        logger = logging.getLogger("debug")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        return logger

    context.register_bean_factory(logger)
    context.register_bean(AspectDependencyPostPrecessor)
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

    @Aspect()
    class LogAdvice(AbstractAdvice):
        def before(self, _pointcut: Pointcut, *_args: Any, **_kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"before {_args}, {_kwargs}")
            return super().before(_pointcut, *_args, **_kwargs)

        def after_raising(self, _pointcut: Pointcut, _error: Exception) -> None:
            nonlocal logs
            logs.append(f"after_raising {_error}")
            return super().after_raising(_pointcut, _error)

        def after_returning(self, _pointcut: Pointcut, _result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {_result}")
            return super().after_returning(_pointcut, _result)

        def after(self, _pointcut: Pointcut) -> None:
            nonlocal logs
            logs.append(f"after")
            return super().after(_pointcut)

        def around(
            self,
            _pointcut: Pointcut,
            func: Callable[P, R],
            *_args: P.args,
            **_kwargs: P.kwargs,
        ) -> R:
            nonlocal logs
            try:
                result: R = super().around(_pointcut, func, *_args, **_kwargs)
            except Exception as e:
                logs.append(f"around {_args}, {_kwargs} {e}")
                raise
            else:
                logs.append(f"around {_args}, {_kwargs} {result}")
                return result

    @dataclass
    class Log(Pointcut):
        advice = LogAdvice

    @Bean()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    @BeanFactory()
    def logger() -> logging.Logger:
        console = logging.StreamHandler()
        console.setLevel(level=logging.DEBUG)
        console.setFormatter(
            logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s")
        )
        logger = logging.getLogger("debug")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        return logger

    context.register_bean_factory(logger)
    context.register_bean(AspectDependencyPostPrecessor)
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

    @Aspect()
    class AsyncLogAdvice(AbstractAsyncAdvice):
        async def before(
            self, _pointcut: AsyncPointcut, *_args: Any, **_kwargs: Any
        ) -> None:
            nonlocal logs
            logs.append(f"before {_args}, {_kwargs}")
            return await super().before(_pointcut, *_args, **_kwargs)

        async def after_raising(
            self, _pointcut: AsyncPointcut, _error: Exception
        ) -> None:
            nonlocal logs
            logs.append(f"after_raising {_error}")
            return await super().after_raising(_pointcut, _error)

        async def after_returning(self, _pointcut: AsyncPointcut, _result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {_result}")
            return await super().after_returning(_pointcut, _result)

        async def after(self, _pointcut: AsyncPointcut) -> None:
            nonlocal logs
            logs.append(f"after")
            return await super().after(_pointcut)

        async def around(
            self,
            _pointcut: AsyncPointcut,
            func: Callable[P, Awaitable[R]],
            *_args: P.args,
            **_kwargs: P.kwargs,
        ) -> R:
            nonlocal logs
            try:
                result: R = await super().around(_pointcut, func, *_args, **_kwargs)
            except Exception as e:
                logs.append(f"around {_args}, {_kwargs} {e}")
                raise
            else:
                logs.append(f"around {_args}, {_kwargs} {result}")
                return result

    @dataclass
    class AsyncLog(AsyncPointcut):
        advice = AsyncLogAdvice

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()

    @BeanFactory()
    def logger() -> logging.Logger:
        console = logging.StreamHandler()
        console.setLevel(level=logging.DEBUG)
        console.setFormatter(
            logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s")
        )
        logger = logging.getLogger("debug")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        return logger

    context.register_bean_factory(logger)
    context.register_bean(AspectDependencyPostPrecessor)
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

    @Aspect()
    class AsyncLogAdvice(AbstractAsyncAdvice):
        async def before(
            self, _pointcut: AsyncPointcut, *_args: Any, **_kwargs: Any
        ) -> None:
            nonlocal logs
            logs.append(f"before {_args}, {_kwargs}")
            return await super().before(_pointcut, *_args, **_kwargs)

        async def after_raising(
            self, _pointcut: AsyncPointcut, _error: Exception
        ) -> None:
            nonlocal logs
            logs.append(f"after_raising {_error}")
            return await super().after_raising(_pointcut, _error)

        async def after_returning(self, _pointcut: AsyncPointcut, _result: Any) -> None:
            nonlocal logs
            logs.append(f"after_returning {_result}")
            return await super().after_returning(_pointcut, _result)

        async def after(self, _pointcut: AsyncPointcut) -> None:
            nonlocal logs
            logs.append(f"after")
            return await super().after(_pointcut)

        async def around(
            self,
            _pointcut: AsyncPointcut,
            func: Callable[P, Awaitable[R]],
            *_args: P.args,
            **_kwargs: P.kwargs,
        ) -> R:
            nonlocal logs
            try:
                result: R = await super().around(_pointcut, func, *_args, **_kwargs)
            except Exception as e:
                logs.append(f"around {_args}, {_kwargs} {e}")
                raise
            else:
                logs.append(f"around {_args}, {_kwargs} {result}")
                return result

    @dataclass
    class AsyncLog(AsyncPointcut):
        advice = AsyncLogAdvice

    @Bean()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            raise RuntimeError

    context: ApplicationContext = ApplicationContext()

    @BeanFactory()
    def logger() -> logging.Logger:
        console = logging.StreamHandler()
        console.setLevel(level=logging.DEBUG)
        console.setFormatter(
            logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s")
        )
        logger = logging.getLogger("debug")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        return logger

    context.register_bean_factory(logger)
    context.register_bean(AspectDependencyPostPrecessor)
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
