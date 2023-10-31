from spakky.framework.context.stereotype.component import Component


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
    assert Component.has_annotation(A)
    assert not Component.has_annotation(B)
    assert Component.has_annotation(C)
    assert not Component.has_annotation(D)
    assert Component.has_annotation(E)
