from logging import Logger

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.application_context import ApplicationContext
from spakky.application.interfaces.pluggable import IPluggable
from spakky.plugins.aspect import AspectPlugin


def test_aspect_plugin_register(logger: Logger) -> None:
    context: ApplicationContext = ApplicationContext()
    plugin: IPluggable = AspectPlugin(logger)
    plugin.register(context)

    assert context.post_processors == {AspectPostProcessor}
