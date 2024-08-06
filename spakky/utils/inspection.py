from inspect import FullArgSpec, ismethod, getfullargspec

from spakky.core.types import Action, Func

SELF = "self"
INIT = "__init__"
PROTOCOL_INIT = "_no_init_or_replace_init"


def is_instance_method(obj: Func) -> bool:
    if ismethod(obj):
        return True
    spec: FullArgSpec = getfullargspec(obj)
    if len(spec.args) > 0 and spec.args[0] == SELF:
        return True
    return False


def has_default_constructor(cls: type[object]) -> bool:
    constructor: Action = getattr(cls, INIT)
    if constructor is object.__init__ or constructor.__name__ == PROTOCOL_INIT:
        # If the constructor is the default constructor
        # or a placeholder for the default constructor
        return True
    return False
