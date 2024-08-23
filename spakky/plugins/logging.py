from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IPodRegistry
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect


class LoggingPlugin(IPluggable):
    def register(self, registry: IPodRegistry) -> None:
        registry.register(LoggingAspect)
        registry.register(AsyncLoggingAspect)
