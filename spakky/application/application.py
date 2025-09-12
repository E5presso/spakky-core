import inspect
import sys
from importlib.metadata import EntryPoints, entry_points
from pathlib import Path
from types import ModuleType
from typing import Callable

from spakky.application.error import AbstractSpakkyApplicationError
from spakky.aspects.logging import AsyncLoggingAspect, LoggingAspect
from spakky.aspects.transactional import AsyncTransactionalAspect, TransactionalAspect
from spakky.core.constants import PLUGIN_PATH
from spakky.core.importing import (
    Module,
    is_package,
    list_modules,
    list_objects,
    resolve_module,
)
from spakky.pod.annotations.pod import Pod, PodType
from spakky.pod.interfaces.application_context import IApplicationContext
from spakky.pod.interfaces.container import IContainer

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


class CannotDetermineScanPathError(AbstractSpakkyApplicationError):
    message = "Cannot determine scan path. Please specify the path explicitly."


class SpakkyApplication:
    _application_context: IApplicationContext

    @property
    def container(self) -> IContainer:
        return self._application_context

    def __init__(self, application_context: IApplicationContext) -> None:
        self._application_context = application_context

    def add(self, obj: PodType) -> Self:
        self._application_context.add(obj)
        return self

    def enable_logging(self) -> Self:
        self.add(LoggingAspect)
        return self

    def enable_async_logging(self) -> Self:
        self.add(AsyncLoggingAspect)
        return self

    def enable_transactional(self) -> Self:
        self.add(TransactionalAspect)
        return self

    def enable_async_transactional(self) -> Self:
        self.add(AsyncTransactionalAspect)
        return self

    def scan(
        self,
        path: Module | None = None,
        exclude: set[Module] | None = None,
    ) -> Self:
        modules: set[ModuleType]
        caller_module: ModuleType | None = None
        if path is None:
            caller_frame = inspect.stack()[1]
            caller_module = inspect.getmodule(caller_frame[0])
            file_path = getattr(caller_module, "__file__", None)
            caller_package = (
                resolve_module(Path(file_path).parent.name) if file_path else None
            )
            if caller_package is None:
                raise CannotDetermineScanPathError
            path = caller_package

        if exclude is None:
            exclude = {caller_module} if caller_module else set()
        if is_package(path):
            modules = list_modules(path, exclude)
        else:
            modules = {resolve_module(path)}

        for module_item in modules:
            for obj in list_objects(module_item, Pod.exists):
                self._application_context.add(obj)

        return self

    def load_plugins(self) -> Self:
        all_entry_points = entry_points()
        my_plugins: EntryPoints = all_entry_points.select(group=PLUGIN_PATH)

        for entry_point in my_plugins:
            entry_point_function: Callable[[SpakkyApplication], None] = (
                entry_point.load()
            )
            entry_point_function(self)
        return self

    def start(self) -> Self:
        self._application_context.start()
        return self

    def stop(self) -> Self:
        self._application_context.stop()
        return self
