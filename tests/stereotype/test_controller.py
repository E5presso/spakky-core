from spakky.stereotype.controller import Controller


def test_controller() -> None:
    @Controller()
    class SampleController: ...

    class NonAnnotated: ...

    assert Controller.get_or_none(SampleController) is not None
    assert Controller.get_or_none(NonAnnotated) is None
