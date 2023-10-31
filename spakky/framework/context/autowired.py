import inspect
from dataclasses import dataclass, field
from inspect import Parameter, Signature, _empty
from spakky.framework.core.annotation import Annotation
from spakky.framework.core.generic import T_OBJ


@dataclass
class Autowired(Annotation):
    dependencies: dict[str, type] = field(init=False, default_factory=dict)

    def __call__(self, obj: T_OBJ) -> T_OBJ:
        signature: Signature = inspect.signature(obj)
        parameters: list[Parameter] = list(signature.parameters.values())
        dependencies: dict[str, type] = {}
        for parameter in parameters:
            parameter_type: type = parameter.annotation
            if parameter_type != _empty:
                dependencies[parameter.name] = parameter_type
        self.dependencies = dependencies
        return self.set_annotation(obj)
