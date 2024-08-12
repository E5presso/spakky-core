from spakky.stereotype.usecase import UseCase


def test_usecase() -> None:
    @UseCase()
    class SampleService: ...

    class NonAnnotated: ...

    assert UseCase.get_or_none(SampleService) is not None
    assert UseCase.get_or_none(NonAnnotated) is None
