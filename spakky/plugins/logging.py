from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry
from spakky.extensions.logging import AsyncLoggingAdvisor, LoggingAdvisor


class LoggingPlugin(IPluggable):
    def register(self, registry: IRegistry) -> None:
        registry.register_bean(LoggingAdvisor)
        registry.register_bean(AsyncLoggingAdvisor)
