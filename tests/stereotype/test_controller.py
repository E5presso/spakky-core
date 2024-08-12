from spakky.stereotype.controller import Controller


def test_controller() -> None:
    @Controller(prefix="/dummy")
    class SampleController: ...

    class NonAnnotated: ...

    assert Controller.get_or_none(SampleController) is not None
    assert Controller.get(SampleController).prefix == "/dummy"
    assert Controller.get_or_none(NonAnnotated) is None
