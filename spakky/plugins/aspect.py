from logging import Logger

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.interfaces.container import IContainer
from spakky.application.interfaces.plugin import IPlugin


class AspectPlugin(IPlugin):
    logger: Logger

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def register(self, container: IContainer) -> None:
        container.register_post_processor(AspectPostProcessor(self.logger))
