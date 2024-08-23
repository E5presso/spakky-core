from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.plugins.logging import LoggingPlugin


def test_logging_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = LoggingPlugin()
    plugin.register(context)

    assert context.pods == {LoggingAspect, AsyncLoggingAspect}
