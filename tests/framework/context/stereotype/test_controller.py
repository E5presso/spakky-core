from spakky.framework.context.stereotype.component import Component, IComponent
from spakky.framework.context.stereotype.controller import Controller, IController
from spakky.framework.web import get


@Controller("/test")
class A:
    @get("")
    async def get_test(self) -> str:
        return "test"


class B:
    ...


@Component()
class C:
    ...


def test_controller_type_checking() -> None:
    assert issubclass(A, IController)
    assert issubclass(A, IComponent)
    assert isinstance(A(), IController)
    assert isinstance(A(), IComponent)
    assert not issubclass(B, IController)
    assert not issubclass(B, IComponent)
    assert not isinstance(B(), IController)
    assert not isinstance(B(), IComponent)

    assert issubclass(C, IComponent)
    assert not issubclass(C, IController)
    assert isinstance(C(), IComponent)
    assert not isinstance(C(), IController)
