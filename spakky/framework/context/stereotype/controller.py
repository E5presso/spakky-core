from dataclasses import dataclass, field
from enum import Enum
import inspect
from types import FunctionType, MethodType
from typing import Any, Callable, Protocol, TypeAlias, runtime_checkable
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field
from spakky.framework.core.generic import T_CLASS, T_OBJ
from .args import EndpointDefinition, EndpointRouteArgs, WebsocketRouteArgs, WebSocketDefinition
from .component import Component


AnyCallable: TypeAlias = Callable[..., Any]


@dataclass
class Controller(Component):
    prefix: str
    tags: list[str | Enum] | None = field(default=None)
    endpoints: list[EndpointDefinition] = field(init=False, default_factory=list)
    websockets: list[WebSocketDefinition] = field(init=False, default_factory=list)

    def __call__(self, obj: T_OBJ) -> T_OBJ:
        endpoints: list[EndpointDefinition] = []
        websockets: list[WebSocketDefinition] = []
        methods: list[MethodType] = list(
            dict(inspect.getmembers(obj, predicate=lambda v: isinstance(v, FunctionType))).values()
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

        self.endpoints = endpoints
        self.websockets = websockets
        return super().__call__(obj)
