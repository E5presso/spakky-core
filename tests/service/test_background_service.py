from asyncio.tasks import sleep as sleep_async
from time import sleep

import pytest

from spakky.application.application_context import ApplicationContext
from spakky.pod.annotations.pod import Pod
from spakky.service.background import (
    AbstractAsyncBackgroundService,
    AbstractBackgroundService,
)


def test_multiple_background_services_graceful_shutdown() -> None:
    ids: list[int] = []

    @Pod()
    class FirstBackgroundService(AbstractBackgroundService):
        __messages: list[int]

        def __init__(self, messages: list[int]) -> None:
            super().__init__()
            self.__messages = messages

        def initialize(self) -> None:
            return

        def dispose(self) -> None:
            return

        def run(self) -> None:
            while self._stop_event.is_set() is False:
                self.__messages.append(1)
                sleep(0.1)

    @Pod()
    class SecondBackgroundService(AbstractBackgroundService):
        __messages: list[int]

        def __init__(self, messages: list[int]) -> None:
            super().__init__()
            self.__messages = messages

        def initialize(self) -> None:
            return

        def dispose(self) -> None:
            return

        def run(self) -> None:
            while self._stop_event.is_set() is False:
                self.__messages.append(2)
                sleep(0.1)

    @Pod()
    def get_messages() -> list[int]:
        return ids

    context = ApplicationContext()
    context.add(get_messages)
    context.add(FirstBackgroundService)
    context.add(SecondBackgroundService)

    context.start()
    sleep(0.1)
    context.stop()

    assert 1 in ids
    assert 2 in ids


@pytest.mark.asyncio
async def test_multiple_async_background_services_graceful_shutdown() -> None:
    ids: list[int] = []

    @Pod()
    class FirstBackgroundService(AbstractAsyncBackgroundService):
        __messages: list[int]

        def __init__(self, messages: list[int]) -> None:
            super().__init__()
            self.__messages = messages

        async def initialize_async(self) -> None:
            return

        async def dispose_async(self) -> None:
            return

        async def run_async(self) -> None:
            while self._stop_event.is_set() is False:
                self.__messages.append(1)
                await sleep_async(0.1)

    @Pod()
    class SecondBackgroundService(AbstractAsyncBackgroundService):
        __messages: list[int]

        def __init__(self, messages: list[int]) -> None:
            super().__init__()
            self.__messages = messages

        async def initialize_async(self) -> None:
            return

        async def dispose_async(self) -> None:
            return

        async def run_async(self) -> None:
            while self._stop_event.is_set() is False:
                self.__messages.append(2)
                await sleep_async(0.1)

    @Pod()
    def get_messages() -> list[int]:
        return ids

    context = ApplicationContext()
    context.add(get_messages)
    context.add(FirstBackgroundService)
    context.add(SecondBackgroundService)

    context.start()
    await sleep_async(0.1)
    context.stop()

    assert 1 in ids
    assert 2 in ids
