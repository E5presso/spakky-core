from spakky.core.annotation import ClassAnnotation
from spakky.injectable.injectable import Injectable


@ClassAnnotation()
class DummyB: ...


@Injectable()
class InjectableB: ...


class UnmanagedB: ...


@Injectable()
def unmanaged_b() -> UnmanagedB:
    return UnmanagedB()


def hello_world() -> str:
    return "Hello World"
