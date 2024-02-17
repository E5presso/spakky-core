from enum import StrEnum, auto
from typing import Any, Callable, Sequence
from dataclasses import field, dataclass

from fastapi import Response, params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.routing import Route as StarletteRoute

from spakky.core.annotation import FunctionAnnotation
from spakky.core.generics import FuncT

SetIntStr = set[int | str]
DictIntStrAny = dict[int | str, Any]


class HTTPMethod(StrEnum):
    GET = auto()
    POST = auto()
    PUT = auto()
    PATCH = auto()
    DELETE = auto()
    HEAD = auto()
    OPTIONS = auto()
    TRACE = auto()


@dataclass
class Route(FunctionAnnotation):
    path: str
    response_model: type[Any] | None = None
    status_code: int | None = None
    tags: list[str] | None = None
    dependencies: Sequence[params.Depends] | None = None
    summary: str | None = None
    description: str | None = None
    response_description: str = "Successful Response"
    responses: dict[int | str, dict[str, Any]] | None = None
    deprecated: bool | None = None
    methods: set[HTTPMethod] | list[HTTPMethod] | None = None
    operation_id: str | None = None
    response_model_include: SetIntStr | DictIntStrAny | None = None
    response_model_exclude: SetIntStr | DictIntStrAny | None = None
    response_model_by_alias: bool = True
    response_model_exclude_unset: bool = False
    response_model_exclude_defaults: bool = False
    response_model_exclude_none: bool = False
    include_in_schema: bool = True
    response_class: type[Response] | DefaultPlaceholder = field(
        default_factory=lambda: Default(JSONResponse)
    )
    name: str | None = None
    route_class_override: type[APIRoute] | None = None
    callbacks: list[StarletteRoute] | None = None
    openapi_extra: dict[str, Any] | None = None


def route(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    methods: set[HTTPMethod] | list[HTTPMethod] | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    def wrapper(method: FuncT) -> FuncT:
        return Route(
            path=path,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            route_class_override=route_class_override,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
        )(method)

    return wrapper


def get(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.GET],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def post(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.POST],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def put(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.PUT],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def patch(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.PATCH],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def delete(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.DELETE],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def head(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.HEAD],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def options(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.OPTIONS],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )


def trace(
    path: str,
    response_model: type[Any] | None = None,
    status_code: int | None = None,
    tags: list[str] | None = None,
    dependencies: Sequence[params.Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: dict[int | str, dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: SetIntStr | DictIntStrAny | None = None,
    response_model_exclude: SetIntStr | DictIntStrAny | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    route_class_override: type[APIRoute] | None = None,
    callbacks: list[StarletteRoute] | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[FuncT], FuncT]:
    return route(
        path=path,
        methods=[HTTPMethod.TRACE],
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        route_class_override=route_class_override,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
    )
