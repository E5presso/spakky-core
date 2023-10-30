from spakky.framework.context.stereotype.component import Component, IComponent


@Component()
class A:
    ...


class B:
    ...


@Component()
class C(B):
    ...


class D:
    ...


@Component()
class E(D, B):
    ...


def test_component_type_checking() -> None:
    assert issubclass(A, IComponent)
    assert isinstance(A(), IComponent)
    assert not issubclass(B, IComponent)
    assert not isinstance(B(), IComponent)

    assert issubclass(C, IComponent)
    assert issubclass(E, IComponent)
