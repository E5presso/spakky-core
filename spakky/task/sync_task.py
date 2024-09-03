from typing import Callable, TypeAlias
from threading import Event, Thread

from spakky.task.cancellation_token import ICancellationToken
from spakky.task.error import TaskAlreadyStartedError, TaskNotStartedError
from spakky.task.interface import ITask

SyncTaskAction: TypeAlias = Callable[[ICancellationToken], None]


class SyncTask(ITask):
    __action: SyncTaskAction
    __cancellation_token: ICancellationToken
    __thread: Thread

    def __init__(
        self,
        action: SyncTaskAction,
        cancellation_token: ICancellationToken | None = None,
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
