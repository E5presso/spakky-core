from spakky.stereotypes.controller import Controller


def test_controller() -> None:
    @Controller(prefix="/dummy")
    class SampleController:
        ...

    class NonAnnotated:
        ...

    assert Controller.single_or_none(SampleController) is not None
    assert Controller.single(SampleController).prefix == "/dummy"
    assert Controller.single_or_none(NonAnnotated) is None
