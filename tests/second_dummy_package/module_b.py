from spakky.bean.bean import Bean
from spakky.core.annotation import ClassAnnotation


@ClassAnnotation()
class SecondDummyB: ...


@Bean()
class SecondComponentB: ...


class SecondUnmanagedB: ...


@Bean()
def unmanaged_b() -> SecondUnmanagedB:
    return SecondUnmanagedB()


def hello_world() -> str:
    return "Hello World"
