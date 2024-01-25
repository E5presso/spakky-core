from spakky.stereotypes.service import Service


def test_service() -> None:
    @Service()
    class SampleService:
        ...

    class NonAnnotated:
        ...

    assert Service.single_or_none(SampleService) is not None
    assert Service.single_or_none(NonAnnotated) is None
