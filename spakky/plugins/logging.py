from spakky.application.interfaces.container import IContainer
from spakky.application.interfaces.plugin import IPlugin
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect


class LoggingPlugin(IPlugin):
    def register(self, container: IContainer) -> None:
        container.register(LoggingAspect)
        container.register(AsyncLoggingAspect)
