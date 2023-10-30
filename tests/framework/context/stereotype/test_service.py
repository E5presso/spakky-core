from spakky.framework.context.stereotype.component import Component, IComponent
from spakky.framework.context.stereotype.service import Service, IService


@Service()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_service_type_checking() -> None:
    assert issubclass(A, IService)
    assert issubclass(A, IComponent)
    assert isinstance(A(), IService)
    assert isinstance(A(), IComponent)
    assert not issubclass(B, IService)
    assert not issubclass(B, IComponent)
    assert not isinstance(B(), IService)
    assert not isinstance(B(), IComponent)

    assert issubclass(C, IComponent)
    assert not issubclass(C, IService)
    assert isinstance(C(), IComponent)
    assert not isinstance(C(), IService)
