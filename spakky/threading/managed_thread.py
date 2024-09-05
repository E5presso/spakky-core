from typing import Optional
from asyncio import Lock as AsyncLock, Event as AsyncEvent, new_event_loop
from threading import Lock as ThreadLock, Event as ThreadEvent, Thread

from spakky.threading.error import ThreadAlreadyStartedError, ThreadNotStartedError
from spakky.threading.interface import (
    IAsyncManagedThreadAction,
    IManagedThread,
    IManagedThreadAction,
)


class ManagedThread(IManagedThread):
    __name: str | None
    __action: IManagedThreadAction
    __event: ThreadEvent
    __lock: ThreadLock
    __thread: Thread | None

    def __init__(
        self,
        action: IManagedThreadAction,
        name: str | None = None,
        event: ThreadEvent | None = None,
        lock: Optional[ThreadLock] = None,
    ) -> None:
        if event is None:
            event = ThreadEvent()
        if lock is None:
            lock = ThreadLock()
        self.__name = name
        self.__action = action
        self.__event = event
        self.__lock = lock
        self.__thread = None

    def start(self) -> None:
        if self.__thread is not None:
            raise ThreadAlreadyStartedError
        self.__thread = Thread(
            name=self.__name,
            target=self.__action,
            args=(self.__event, self.__lock),
        )
        self.__thread.start()

    def stop(self) -> None:
        if self.__thread is None:
            raise ThreadNotStartedError
        self.__event.set()
        self.__thread.join()
        self.__event.clear()
        self.__thread = None


class AsyncManagedThread(IManagedThread):
    __name: str | None
    __action: IAsyncManagedThreadAction
    __event: AsyncEvent
    __lock: AsyncLock
    __thread: Thread | None

    def __init__(
        self,
        action: IAsyncManagedThreadAction,
        name: str | None = None,
        event: AsyncEvent | None = None,
        lock: Optional[AsyncLock] = None,
    ) -> None:
        if event is None:
            event = AsyncEvent()
        if lock is None:
            lock = AsyncLock()
        self.__name = name
        self.__action = action
        self.__event = event
        self.__lock = lock
        self.__thread = None

    def __run(self) -> None:
        event_loop = new_event_loop()
        event_loop.run_until_complete(self.__action(self.__event, self.__lock))
        event_loop.close()

    def start(self) -> None:
        if self.__thread is not None:
            raise ThreadAlreadyStartedError
        self.__thread = Thread(name=self.__name, target=self.__run)
        self.__thread.start()

    def stop(self) -> None:
        if self.__thread is None:
            raise ThreadNotStartedError
        self.__event.set()
        self.__thread.join()
        self.__event.clear()
        self.__thread = None
