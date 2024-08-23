from spakky.core.annotation import ClassAnnotation
from spakky.pod.pod import Pod


@ClassAnnotation()
class SecondDummyB: ...


@Pod()
class SecondPodB: ...


class SecondUnmanagedB: ...


@Pod()
def unmanaged_b() -> SecondUnmanagedB:
    return SecondUnmanagedB()


def hello_world() -> str:
    return "Hello World"
