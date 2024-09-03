from typing import Callable, Awaitable, TypeAlias
from asyncio import Event, AbstractEventLoop, new_event_loop
from threading import Thread

from spakky.task.error import TaskAlreadyStartedError, TaskNotStartedError
from spakky.task.interface import ITask

AsyncTaskAction: TypeAlias = Callable[[Event], Awaitable[None]]


class AsyncTask(ITask):
    __action: AsyncTaskAction
    __event_loop: AbstractEventLoop
    __cancellation_token: Event
    __thread: Thread

    def __init__(
        self,
        action: AsyncTaskAction,
        cancellation_token: Event | None = None,
    ) -> None:
        if cancellation_token is None:
            cancellation_token = Event()
        self.__action = action
        self.__event_loop = new_event_loop()
        self.__cancellation_token = cancellation_token
        self.__thread = Thread(
            target=self.__event_loop.run_until_complete,
            args=(self.__action(self.__cancellation_token),),
        )

    def start(self) -> None:
        if self.__thread.ident is not None:
            raise TaskAlreadyStartedError
        self.__thread.start()

    def stop(self) -> None:
        if self.__thread.ident is None:
            raise TaskNotStartedError
        self.__cancellation_token.set()
        self.__thread.join()
        self.__event_loop.close()
