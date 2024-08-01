import pytest

from spakky.bean.application_context import ApplicationContext
from spakky.cryptography.key import Key
from tests.aop.apps.dummy import AsyncDummyUseCase, DummyUseCase


def test_post_processor_with_complete_application_context(
    application_context: ApplicationContext,
) -> None:
    usecase: DummyUseCase = application_context.single(required_type=DummyUseCase)

    assert usecase.execute() == "Hello, World!"
    assert usecase.key == application_context.single(required_type=Key)


@pytest.mark.asyncio
async def test_post_processor_with_complete_application_context_async(
    application_context: ApplicationContext,
) -> None:
    usecase: AsyncDummyUseCase = application_context.single(
        required_type=AsyncDummyUseCase
    )

    assert await usecase.execute() == "Hello, World!"
    assert usecase.key == application_context.single(required_type=Key)
