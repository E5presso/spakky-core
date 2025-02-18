from spakky.application.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.aware.container_aware import IContainerAware
from spakky.pod.interfaces.post_processor import IPostProcessor


class ApplicationContextAwareProcessor(IPostProcessor):
    __application_context: IApplicationContext

    def __init__(self, application_context: IApplicationContext) -> None:
        self.__application_context = application_context

    def post_process(self, pod: object) -> object:
        if isinstance(pod, IContainerAware):
            pod.set_container(self.__application_context)
        return pod
