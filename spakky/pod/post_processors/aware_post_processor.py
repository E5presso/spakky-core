from logging import Logger

from spakky.pod.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.aware.application_context_aware import (
    IApplicationContextAware,
)
from spakky.pod.interfaces.aware.container_aware import IContainerAware
from spakky.pod.interfaces.aware.logger_aware import ILoggerAware
from spakky.pod.interfaces.post_processor import IPostProcessor


class ApplicationContextAwareProcessor(IPostProcessor):
    __application_context: IApplicationContext
    __logger: Logger

    def __init__(
        self, application_context: IApplicationContext, logger: Logger
    ) -> None:
        self.__application_context = application_context
        self.__logger = logger

    def post_process(self, pod: object) -> object:
        if isinstance(pod, IContainerAware):
            pod.set_container(self.__application_context)
        if isinstance(pod, IApplicationContextAware):
            pod.set_application_context(self.__application_context)
        if isinstance(pod, ILoggerAware):
            pod.set_logger(self.__logger)
        return pod
