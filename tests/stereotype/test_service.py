from spakky.stereotype.usecase import UseCase


def test_service() -> None:
    @UseCase()
    class SampleService:
        ...

    class NonAnnotated:
        ...

    assert UseCase.single_or_none(SampleService) is not None
    assert UseCase.single_or_none(NonAnnotated) is None
