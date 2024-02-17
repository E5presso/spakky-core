import logging

from fastapi import FastAPI

import sample
from spakky.aop.post_processor import AspectDependencyPostPrecessor
from spakky.dependency.application_context import ApplicationContext
from spakky.plugin.fastapi.post_processor import FastAPIDependencyPostProcessor

app: FastAPI = FastAPI()
context: ApplicationContext = ApplicationContext(package=sample)

context.add_post_processor(AspectDependencyPostPrecessor())
context.add_post_processor(FastAPIDependencyPostProcessor(app))

console = logging.StreamHandler()
console.setLevel(level=logging.DEBUG)
console.setFormatter(logging.Formatter("[%(levelname)s][%(asctime)s]: %(message)s"))
logger = logging.getLogger("debug")
logger.setLevel(logging.DEBUG)
logger.addHandler(console)
context.register_unmanaged_dependency("logger", logger)

context.initialize()
