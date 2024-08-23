from logging import Logger

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IPodRegistry


class AspectPlugin(IPluggable):
    logger: Logger

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def register(self, registry: IPodRegistry) -> None:
        registry.register_post_processor(AspectPostProcessor(self.logger))
