from enum import Enum
import inspect
from types import FunctionType, MethodType
from typing import Any, Callable, Protocol, TypeAlias, runtime_checkable
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field
from spakky.framework.core.generic import T_CLASS
from .args import EndpointDefinition, EndpointRouteArgs, WebsocketRouteArgs, WebSocketDefinition
from .component import Component, IComponent


AnyCallable: TypeAlias = Callable[..., Any]


@runtime_checkable
class IController(IComponent, Protocol):
    __controller__: bool
    __prefix__: str
    __tags__: list[str | Enum] | None
    __endpoints__: list[EndpointDefinition]
    __websockets__: list[WebSocketDefinition]

    def __instancecheck__(self, __instance: Any) -> bool:
        return (
            super().__instancecheck__(__instance)
            and hasattr(__instance, "__controller__")
            and hasattr(__instance, "__prefix__")
            and hasattr(__instance, "__tags__")
            and hasattr(__instance, "__endpoints__")
            and hasattr(__instance, "__websockets__")
        )

    @classmethod
    def __subclasshook__(cls, __subclass: type) -> bool:
        return (
            super().__subclasshook__(__subclass)
            and hasattr(__subclass, "__controller__")
            and hasattr(__subclass, "__prefix__")
            and hasattr(__subclass, "__tags__")
            and hasattr(__subclass, "__endpoints__")
            and hasattr(__subclass, "__websockets__")
        )


class Controller(Component):
    _prefix: str
    _tags: list[str | Enum] | None

    def __init__(
        self,
        prefix: str,
        tags: list[str | Enum] | str | Enum | None = None,
    ) -> None:
        super().__init__()
        self._prefix = prefix
        if isinstance(tags, str) or isinstance(tags, Enum):
            tags = [tags]
        self._tags = tags

    def __call__(self, cls: T_CLASS) -> T_CLASS:
        cls = super().__call__(cls)
        endpoints: list[EndpointDefinition] = []
        websockets: list[WebSocketDefinition] = []
        methods: list[MethodType] = list(
            dict(inspect.getmembers(cls, predicate=lambda v: isinstance(v, FunctionType))).values()
        )
        for method in methods:
            if hasattr(method, "_endpoint"):
                endpoint: EndpointDefinition = getattr(method, "_endpoint")
                endpoint_method: Callable[..., Any] = endpoint.method
                endpoint_args: EndpointRouteArgs = endpoint.args
                return_type: type[Any] | None = inspect.signature(endpoint_method).return_annotation
                if endpoint.args.name is None:
                    endpoint.args.name = " ".join([x.capitalize() for x in endpoint.method.__name__.split("_")])
                if endpoint.args.description is None:
                    endpoint.args.description = endpoint.method.__doc__
                if return_type is not None:
                    try:
                        create_response_field("", return_type)
                    except FastAPIError:
                        ...
                    else:
                        endpoint_args.response_model = return_type
                endpoints.append(EndpointDefinition(method=endpoint_method, args=endpoint_args))
            elif hasattr(method, "_websocket"):
                websocket: WebSocketDefinition = getattr(method, "_websocket")
                websocket_method: Callable[..., Any] = websocket.method
                websocket_args: WebsocketRouteArgs = websocket.args
                if websocket.args.name is None:
                    websocket.args.name = " ".join([x.capitalize() for x in websocket.method.__name__.split("_")])
                websockets.append(WebSocketDefinition(method=websocket_method, args=websocket_args))
        setattr(cls, "__controller__", True)
        setattr(cls, "__prefix__", self._prefix)
        setattr(cls, "__tags__", self._tags)
        setattr(cls, "__endpoints__", endpoints)
        setattr(cls, "__websockets__", websockets)
        return cls
