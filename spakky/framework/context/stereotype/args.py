from typing import Any, Callable, Sequence, Type, TypeAlias
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass
from starlette.routing import Route
from fastapi import Response, params
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.datastructures import Default, DefaultPlaceholder

SetIntStr: TypeAlias = set[int | str]
DictIntStrAny: TypeAlias = dict[int | str, Any]
AnyCallable: TypeAlias = Callable[..., Any]


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class EndpointRouteArgs:
    path: str
    response_model: Type[Any] | None = None
    status_code: int | None = None
    tags: list[str] | None = None
    dependencies: Sequence[params.Depends] | None = None
    summary: str | None = None
    description: str | None = None
    response_description: str = "Successful Response"
    responses: dict[int | str, dict[str, Any]] | None = None
    deprecated: bool | None = None
    methods: set[str] | list[str] | None = None
    operation_id: str | None = None
    response_model_include: SetIntStr | DictIntStrAny | None = None
    response_model_exclude: SetIntStr | DictIntStrAny | None = None
    response_model_by_alias: bool = True
    response_model_exclude_unset: bool = False
    response_model_exclude_defaults: bool = False
    response_model_exclude_none: bool = False
    include_in_schema: bool = True
    response_class: Type[Response] | DefaultPlaceholder = Field(default_factory=lambda: Default(JSONResponse))
    name: str | None = None
    route_class_override: Type[APIRoute] | None = None
    callbacks: list[Route] | None = None
    openapi_extra: dict[str, Any] | None = None


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class WebsocketRouteArgs:
    path: str
    name: str | None


@dataclass
class EndpointDefinition:
    method: AnyCallable
    args: EndpointRouteArgs


@dataclass
class WebSocketDefinition:
    method: AnyCallable
    args: WebsocketRouteArgs
