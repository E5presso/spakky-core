from typing import Any
from dataclasses import dataclass

import pytest

from spakky.aop.advice import Advice, Aspect, AsyncAdvice, AsyncPointcut, Pointcut
from spakky.aop.post_processor import AspectDependencyPostPrecessor
from spakky.dependency.application_context import ApplicationContext
from spakky.dependency.component import Component


def test_aspect_post_processor() -> None:
    logs: list[str] = []

    @Aspect()
    class LogAdvisor(Advice):
        def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"{_args}, {_kwargs}")
            return super().before(*_args, **_kwargs)

    @dataclass
    class Log(Pointcut):
        advice = LogAdvisor

    @Component()
    class EchoService:
        @Log()
        def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()
    context.register_component(EchoService)
    context.register_component(LogAdvisor)
    context.add_post_processor(AspectDependencyPostPrecessor())
    context.initialize()

    service: EchoService = context.get(required_type=EchoService)
    assert service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "(), {'message': 'Hello World!'}"


@pytest.mark.asyncio
async def test_async_aspect_post_processor() -> None:
    logs: list[str] = []

    @Aspect()
    class AsyncLogAdvisor(AsyncAdvice):
        async def before(self, *_args: Any, **_kwargs: Any) -> None:
            nonlocal logs
            logs.append(f"{_args}, {_kwargs}")
            return await super().before(*_args, **_kwargs)

    @dataclass
    class AsyncLog(AsyncPointcut):
        advice = AsyncLogAdvisor

    @Component()
    class EchoService:
        @AsyncLog()
        async def echo(self, message: str) -> str:
            return message

    context: ApplicationContext = ApplicationContext()
    context.register_component(EchoService)
    context.register_component(AsyncLogAdvisor)
    context.add_post_processor(AspectDependencyPostPrecessor())
    context.initialize()

    service: EchoService = context.get(required_type=EchoService)
    assert await service.echo(message="Hello World!") == "Hello World!"
    assert logs[0] == "(), {'message': 'Hello World!'}"
