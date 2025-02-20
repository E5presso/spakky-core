from logging import Logger

from spakky.pod.annotations.pod import Pod
from spakky.pod.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.post_processor import IPostProcessor
from spakky.service.interfaces.service import IAsyncService, IService


@Pod()
class ServicePostProcessor(IPostProcessor):
    __application_context: IApplicationContext
    __logger: Logger

    def __init__(
        self, application_context: IApplicationContext, logger: Logger
    ) -> None:
        super().__init__()
        self.__application_context = application_context
        self.__logger = logger

    def post_process(self, pod: object) -> object:
        if isinstance(pod, IService):
            pod.set_stop_event(self.__application_context.thread_stop_event)
            self.__application_context.add_service(pod)
            self.__logger.debug(
                (f"[{type(self).__name__}] {type(pod).__name__!r} added to container")
            )
        if isinstance(pod, IAsyncService):
            pod.set_stop_event(self.__application_context.task_stop_event)
            self.__application_context.add_service(pod)
            self.__logger.debug(
                (f"[{type(self).__name__}] {type(pod).__name__!r} added to container")
            )
        return pod
