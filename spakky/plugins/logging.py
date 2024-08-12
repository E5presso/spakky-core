from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect


class LoggingPlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_injectable(LoggingAspect)
        registry.register_injectable(AsyncLoggingAspect)
