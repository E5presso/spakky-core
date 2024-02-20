from typing import Any
from inspect import signature, getmembers, isfunction
from logging import Logger
from dataclasses import asdict

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field  # type: ignore

from spakky.dependency.autowired import autowired
from spakky.dependency.interfaces.dependency_container import IDependencyContainer
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)
from spakky.dependency.plugin import Plugin
from spakky.plugin.fastapi.routing import Route
from spakky.stereotypes.controller import Controller


@Plugin()
class FastAPIDependencyPostProcessor(IDependencyPostProcessor):
    __logger: Logger

    @autowired
    def __init__(self, app: FastAPI, logger: Logger) -> None:
        self.__app = app
        self.__logger = logger

    def process_dependency(self, container: IDependencyContainer, dependency: Any) -> Any:
        if Controller.contains(dependency):
            controller = Controller.single(dependency)
            router: APIRouter = APIRouter(prefix=controller.prefix)
            methods = getmembers(dependency, isfunction)
            for name, method in methods:
                if not Route.contains(method):
                    continue
                route = Route.single(method)
                self.__logger.info(
                    f"[{type(self).__name__}] {route.methods} {controller.prefix}{route.path} -> {method.__qualname__}"
                )
                if route.name is None:
                    route.name = " ".join([x.capitalize() for x in name.split("_")])
                if route.description is None:
                    route.description = method.__doc__
                if route.response_model is None:
                    return_annotation: type | None = signature(method).return_annotation
                    if return_annotation is not None:
                        try:
                            create_response_field("", return_annotation)
                        except FastAPIError:
                            pass
                        else:
                            route.response_model = return_annotation
                router.add_api_route(endpoint=method, **asdict(route))
            self.__app.include_router(router)
        return dependency
