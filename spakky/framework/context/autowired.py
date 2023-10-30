import inspect
from inspect import Parameter, Signature, _empty

from spakky.framework.core.generic import T_FUNC


class Autowired:
    def __call__(self, function: T_FUNC) -> T_FUNC:
        signature: Signature = inspect.signature(function)
        parameters: list[Parameter] = list(signature.parameters.values())
        autowired: dict[str, type] = {}
        for parameter in parameters:
            parameter_type: type = parameter.annotation
            if parameter_type != _empty:
                autowired[parameter.name] = parameter_type
        setattr(function, "__autowired__", autowired)
        return function
