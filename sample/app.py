import logging

import sample
from spakky.aop.post_processor import AspectDependencyPostPrecessor
from spakky.dependency.application_context import ApplicationContext

context: ApplicationContext = ApplicationContext(package=sample)
context.add_post_processor(AspectDependencyPostPrecessor())

logger: logging.Logger = logging.getLogger("simple_example")
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(level=logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s] (%(asctime)s) : %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
context.register_unmanaged_dependency("logger", logger)

context.initialize()
