import asyncio

import pytest

from spakky.application.application_context import ApplicationContext
from spakky.pod.annotations.pod import Pod


def test_get_singleton_scoped_pod() -> None:
    @Pod(scope=Pod.Scope.SINGLETON)
    class A: ...

    context = ApplicationContext()
    context.add(A)

    context.start()

    a1 = context.get(A)
    a2 = context.get(A)

    assert a1 is a2


def test_get_prototype_scoped_pod() -> None:
    @Pod(scope=Pod.Scope.PROTOTYPE)
    class A: ...

    context = ApplicationContext()
    context.add(A)

    context.start()

    a1 = context.get(A)
    a2 = context.get(A)

    assert a1 is not a2


@pytest.mark.asyncio
async def test_context_scoped_pod_creates_isolated_instances_per_async_flow() -> None:
    @Pod(scope=Pod.Scope.CONTEXT)
    class A: ...

    context = ApplicationContext()
    context.add(A)
    context.start()

    results: list[A] = []

    async def task_logic() -> None:
        context.clear_context()
        instance1 = context.get(A)
        await asyncio.sleep(0.01)
        instance2 = context.get(A)
        assert instance1 is instance2
        results.append(instance1)

    await asyncio.gather(*(task_logic() for _ in range(5)))
    assert len(set(map(id, results))) == 5
