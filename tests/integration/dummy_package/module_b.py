from spakky.bean.bean import Bean, BeanFactory
from spakky.core.annotation import ClassAnnotation


@ClassAnnotation()
class DummyB:
    ...


@Bean()
class ComponentB:
    ...


class UnmanagedB:
    ...


@BeanFactory()
def unmanaged_b() -> UnmanagedB:
    return UnmanagedB()


def hello_world() -> str:
    return "Hello World"
