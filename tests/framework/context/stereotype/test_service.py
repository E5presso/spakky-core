from spakky.framework.context.stereotype.component import Component
from spakky.framework.context.stereotype.service import Service


@Service()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_service_type_checking() -> None:
    assert Component.has_annotation(A)
    assert Service.has_annotation(A)
    assert not Component.has_annotation(B)
    assert not Service.has_annotation(B)

    assert Component.has_annotation(C)
    assert not Service.has_annotation(C)
