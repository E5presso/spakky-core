from typing import Callable, TypeAlias
from threading import Event, Thread

from spakky.task.error import TaskAlreadyStartedError, TaskNotStartedError
from spakky.task.interface import ITask

SyncTaskAction: TypeAlias = Callable[[Event], None]


class SyncTask(ITask):
    __action: SyncTaskAction
    __cancellation_token: Event
    __thread: Thread

    def __init__(
        self,
        action: SyncTaskAction,
        cancellation_token: Event | None = None,
    ) -> None:
        if cancellation_token is None:
            cancellation_token = Event()
        self.__action = action
        self.__cancellation_token = cancellation_token
        self.__thread = Thread(
            target=self.__action,
            args=(self.__cancellation_token,),
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
