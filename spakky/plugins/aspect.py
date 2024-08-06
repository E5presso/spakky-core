from logging import Logger

from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.application.interfaces.pluggable import IPluggable
from spakky.application.interfaces.registry import IRegistry


class AspectPlugin(IPluggable):
    logger: Logger

    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def register(self, registry: IRegistry) -> None:
        registry.register_bean_post_processor(AspectBeanPostProcessor(self.logger))
