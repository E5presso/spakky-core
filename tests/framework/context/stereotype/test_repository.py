from spakky.framework.context.stereotype.component import Component
from spakky.framework.context.stereotype.repository import Repository


@Repository()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_repository_type_checking() -> None:
    assert Component.has_annotation(A)
    assert Repository.has_annotation(A)
    assert not Component.has_annotation(B)
    assert not Repository.has_annotation(B)

    assert Component.has_annotation(C)
    assert not Repository.has_annotation(C)
