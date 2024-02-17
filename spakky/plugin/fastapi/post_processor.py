from typing import Any
from inspect import ismethod, signature, getmembers
from functools import partial
from dataclasses import asdict

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import FastAPIError
from fastapi.utils import create_response_field  # type: ignore

from spakky.dependency.interfaces.dependency_container import IDependencyContainer
from spakky.dependency.interfaces.dependency_post_processor import (
    IDependencyPostProcessor,
)
from spakky.plugin.fastapi.routing import Route
from spakky.stereotypes.controller import Controller


class FastAPIDependencyPostProcessor(IDependencyPostProcessor):
    __app: FastAPI

    def __init__(self, app: FastAPI) -> None:
        self.__app = app

    def process_dependency(self, container: IDependencyContainer, dependency: Any) -> Any:
        if Controller.contains(dependency):
            controller = Controller.single(dependency)
            router: APIRouter = APIRouter(prefix=controller.prefix)
            for name, method in getmembers(dependency, ismethod):
                if not Route.contains(method):
                    continue
                route = Route.single(method)
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
                router.add_api_route(
                    endpoint=partial(method, dependency), **asdict(route)
                )
            self.__app.include_router(router)
        return dependency
