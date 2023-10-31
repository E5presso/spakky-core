from dataclasses import dataclass, field
from types import ModuleType
from spakky.framework.context.application_context import ApplicationContext
from spakky.framework.context.stereotype.component import Component
from spakky.framework.core.annotation import Annotation
from spakky.framework.core.generic import T_OBJ
from spakky.framework.core.importing import full_scan_modules, get_module, list_classes


class CannotScanCurrentModuleException(Exception):
    def __repr__(self) -> str:
        return f"Cannot scan current module"


@dataclass
class ComponentScan(Annotation):
    context: ApplicationContext = field(init=False, default_factory=ApplicationContext)
    base_packages: list[str] = field(default_factory=list)

    def __call__(self, obj: T_OBJ) -> T_OBJ:
        current_path: str | None = get_module(obj).__file__
        if current_path is None:
            raise CannotScanCurrentModuleException
        modules: set[ModuleType] = full_scan_modules([current_path] + self.base_packages)
        components: set[type] = set()
        for module in modules:
            [components.add(x) for x in list_classes(module, lambda x: Component.has_annotation(x))]
        [self.context.register(x) for x in components]
        self.set_annotation(obj)
        return obj
