from asyncio import Lock as AsyncLock, Event as AsyncEvent
from threading import Lock as ThreadLock, Event as ThreadEvent

import pytest

from spakky.threading.error import ThreadAlreadyStartedError, ThreadNotStartedError
from spakky.threading.interface import IManagedThread
from spakky.threading.managed_thread import AsyncManagedThread, ManagedThread

NUMBER_OF_ITERATIONS: int = 100


def test_managed_thread() -> None:
    lock: ThreadLock = ThreadLock()
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    thread: IManagedThread = ManagedThread(action, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS


def test_managed_thread_multiple_times() -> None:
    lock: ThreadLock = ThreadLock()
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    thread: IManagedThread = ManagedThread(action, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS

    thread.start()
    while number < NUMBER_OF_ITERATIONS * 2:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS * 2


def test_managed_thread_without_lock() -> None:
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    thread: IManagedThread = ManagedThread(action)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS


def test_managed_thread_with_external_event() -> None:
    lock: ThreadLock = ThreadLock()
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    event: ThreadEvent = ThreadEvent()
    thread: IManagedThread = ManagedThread(action, event=event, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    event.set()
    assert number >= NUMBER_OF_ITERATIONS


def test_managed_thread_start_with_already_started_thread() -> None:
    lock: ThreadLock = ThreadLock()
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    thread: IManagedThread = ManagedThread(action, lock=lock)
    thread.start()
    with pytest.raises(ThreadAlreadyStartedError):
        thread.start()
    thread.stop()


def test_managed_thread_stop_with_not_started_thread() -> None:
    lock: ThreadLock = ThreadLock()
    number: int = 0

    def action(event: ThreadEvent, lock: ThreadLock) -> None:
        nonlocal number
        while not event.is_set():
            with lock:
                number += 1

    thread: IManagedThread = ManagedThread(action, lock=lock)
    with pytest.raises(ThreadNotStartedError):
        thread.stop()


@pytest.mark.asyncio
async def test_async_managed_thread() -> None:
    number: int = 0
    lock: AsyncLock = AsyncLock()

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    thread: IManagedThread = AsyncManagedThread(action, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS


@pytest.mark.asyncio
async def test_async_managed_thread_multiple_times() -> None:
    number: int = 0
    lock: AsyncLock = AsyncLock()

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    thread: IManagedThread = AsyncManagedThread(action, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS

    thread.start()
    while number < NUMBER_OF_ITERATIONS * 2:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS * 2


@pytest.mark.asyncio
async def test_async_managed_thread_without_lock() -> None:
    number: int = 0

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    thread: IManagedThread = AsyncManagedThread(action)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    thread.stop()
    assert number >= NUMBER_OF_ITERATIONS


@pytest.mark.asyncio
async def test_async_managed_thread_with_external_event() -> None:
    number: int = 0
    lock: AsyncLock = AsyncLock()

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    event: AsyncEvent = AsyncEvent()
    thread: IManagedThread = AsyncManagedThread(action, event=event, lock=lock)
    thread.start()
    while number < NUMBER_OF_ITERATIONS:
        pass
    event.set()
    assert number >= NUMBER_OF_ITERATIONS


@pytest.mark.asyncio
async def test_async_managed_thread_start_with_already_started_thread() -> None:
    number: int = 0
    lock: AsyncLock = AsyncLock()

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    thread: IManagedThread = AsyncManagedThread(action, lock=lock)
    thread.start()
    with pytest.raises(ThreadAlreadyStartedError):
        thread.start()
    thread.stop()


@pytest.mark.asyncio
async def test_async_managed_thread_stop_with_not_started_thread() -> None:
    number: int = 0
    lock: AsyncLock = AsyncLock()

    async def action(event: AsyncEvent, lock: AsyncLock) -> None:
        nonlocal number
        while not event.is_set():
            async with lock:
                number += 1

    thread: IManagedThread = AsyncManagedThread(action, lock=lock)
    with pytest.raises(ThreadNotStartedError):
        thread.stop()
