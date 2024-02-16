import sample
from spakky.aop.post_processor import AspectDependencyPostPrecessor
from spakky.dependency.application_context import ApplicationContext

context: ApplicationContext = ApplicationContext(package=sample)
context.add_post_processor(AspectDependencyPostPrecessor())
context.initialize()
