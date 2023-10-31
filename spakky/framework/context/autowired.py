import inspect
from dataclasses import dataclass, field
from inspect import Parameter, Signature
from spakky.framework.core.annotation import Annotation
from spakky.framework.core.generic import T_INIT


@dataclass
class Autowired(Annotation):
    dependencies: dict[str, type] = field(init=False, default_factory=dict)

    def __call__(self, obj: T_INIT) -> T_INIT:
        if obj.__name__ != "__init__":
            raise RuntimeError("Autowired should be decorated on constructor")
        signature: Signature = inspect.signature(obj)
        parameters: list[Parameter] = list(signature.parameters.values())
        dependencies: dict[str, type] = {}
        for parameter in parameters:
            parameter_type: type = parameter.annotation
            if parameter_type != Parameter.empty:
                dependencies[parameter.name] = parameter_type
        self.dependencies = dependencies
        return self.set_annotation(obj)
