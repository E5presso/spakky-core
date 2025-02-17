import sys
from types import ModuleType
from typing import Callable
from logging import Logger
from importlib.metadata import EntryPoints, SelectableGroups, entry_points

from spakky.aop.post_processor import AspectPostProcessor
from spakky.application.error import SpakkyApplicationError
from spakky.application.interfaces.application_context import IApplicationContext
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect
from spakky.constants import PLUGIN_PATH
from spakky.core.importing import (
    Module,
    is_package,
    list_modules,
    list_objects,
    resolve_module,
)
from spakky.pod.interfaces.container import IContainer
from spakky.pod.pod import Pod, PodType

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


class LoggerNotRegisteredError(SpakkyApplicationError):
    message = "Logger is not registered"


class AOPNotEnabledError(SpakkyApplicationError):
    message = "AOP is not enabled"


class SpakkyApplication:
    _application_context: IApplicationContext

    @property
    def container(self) -> IContainer:
        return self._application_context

    @property
    def is_logger_registered(self) -> bool:
        return self._application_context.contains(type_=Logger)

    @property
    def is_aop_enabled(self) -> bool:
        return self._application_context.contains(type_=AspectPostProcessor)

    def __init__(self, application_context: IApplicationContext) -> None:
        self._application_context = application_context

    def register(self, obj: PodType) -> Self:
        self._application_context.add(obj)
        return self

    def register_logger(self, name: str, logger: Logger) -> Self:
        self._application_context.add_singleton_instance(name, logger)
        return self

    def enable_aop(self) -> Self:
        if not self.is_logger_registered:
            raise LoggerNotRegisteredError
        self.register(AspectPostProcessor)
        return self

    def enable_logging_aspect(self) -> Self:
        if not self.is_aop_enabled:
            raise AOPNotEnabledError
        self.register(LoggingAspect)
        self.register(AsyncLoggingAspect)
        return self

    def enable_transaction_aspect(self) -> Self:
        if not self.is_aop_enabled:
            raise AOPNotEnabledError
        self.register(TransactionalAspect)
        self.register(AsyncTransactionalAspect)
        return self

    def scan(self, path: Module, exclude: set[Module] | None = None) -> Self:
        modules: set[ModuleType]
        if exclude is None:
            exclude = set()

        if is_package(path):
            modules = list_modules(path, exclude)
        else:
            modules = {resolve_module(path)}

        for module_item in modules:
            for obj in list_objects(module_item, Pod.exists):
                self.register(obj)

        return self

    def load_plugins(self) -> Self:
        all_entry_points: SelectableGroups = entry_points()
        my_plugins: EntryPoints = all_entry_points.select(group=PLUGIN_PATH)

        for entry_point in my_plugins:
            entry_point_function: Callable[[SpakkyApplication], None] = entry_point.load()
            entry_point_function(self)
        return self

    def start(self) -> Self:
        self._application_context.start()
        return self

    def stop(self) -> Self:
        self._application_context.stop()
        return self
