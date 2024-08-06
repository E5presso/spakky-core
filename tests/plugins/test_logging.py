from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable
from spakky.extensions.logging import AsyncLoggingAdvisor, LoggingAdvisor
from spakky.plugins.logging import LoggingPlugin


def test_logging_plugin_register() -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = LoggingPlugin()
    plugin.register(context)

    assert context.beans == {LoggingAdvisor, AsyncLoggingAdvisor}
