from spakky.framework.context.stereotype.component import Component
from spakky.framework.context.stereotype.controller import Controller
from spakky.framework.web import get


@Controller("/dummy")
class A:
    @get("")
    async def get_dummy(self) -> str:
        return "dummy"


class B:
    ...


@Component()
class C:
    ...


def test_controller_type_checking() -> None:
    assert Component.has_annotation(A)
    assert Controller.has_annotation(A)
    assert not Component.has_annotation(B)
    assert not Controller.has_annotation(B)

    assert Component.has_annotation(C)
    assert not Controller.has_annotation(C)
