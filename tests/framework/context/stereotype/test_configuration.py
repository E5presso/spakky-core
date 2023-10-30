from spakky.framework.context.stereotype.component import Component, IComponent
from spakky.framework.context.stereotype.configuration import Configuration, IConfiguration


@Configuration()
class A:
    ...


class B:
    ...


@Component()
class C:
    ...


def test_configuration_type_checking() -> None:
    assert issubclass(A, IConfiguration)
    assert issubclass(A, IComponent)
    assert isinstance(A(), IConfiguration)
    assert isinstance(A(), IComponent)
    assert not issubclass(B, IConfiguration)
    assert not issubclass(B, IComponent)
    assert not isinstance(B(), IConfiguration)
    assert not isinstance(B(), IComponent)

    assert issubclass(C, IComponent)
    assert not issubclass(C, IConfiguration)
    assert isinstance(C(), IComponent)
    assert not isinstance(C(), IConfiguration)
