from spakky.framework.context.stereotype.component import Component
from spakky.framework.context.stereotype.configuration import Configuration


@Configuration()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_configuration_type_checking() -> None:
    assert Component.has_annotation(A)
    assert Configuration.has_annotation(A)

    assert not Component.has_annotation(B)
    assert not Configuration.has_annotation(B)

    assert Component.has_annotation(C)
    assert not Configuration.has_annotation(C)
