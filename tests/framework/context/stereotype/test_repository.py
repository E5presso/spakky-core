from spakky.framework.context.stereotype.component import Component, IComponent
from spakky.framework.context.stereotype.repository import Repository, IRepository


@Repository()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_repository_type_checking() -> None:
    assert issubclass(A, IRepository)
    assert issubclass(A, IComponent)
    assert isinstance(A(), IRepository)
    assert isinstance(A(), IComponent)
    assert not issubclass(B, IRepository)
    assert not issubclass(B, IComponent)
    assert not isinstance(B(), IRepository)
    assert not isinstance(B(), IComponent)

    assert issubclass(C, IComponent)
    assert not issubclass(C, IRepository)
    assert isinstance(C(), IComponent)
    assert not isinstance(C(), IRepository)
