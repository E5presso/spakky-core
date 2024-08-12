from spakky.core.annotation import ClassAnnotation
from spakky.injectable.injectable import Injectable


@ClassAnnotation()
class SecondDummyB: ...


@Injectable()
class SecondInjectableB: ...


class SecondUnmanagedB: ...


@Injectable()
def unmanaged_b() -> SecondUnmanagedB:
    return SecondUnmanagedB()


def hello_world() -> str:
    return "Hello World"
