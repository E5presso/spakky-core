from spakky.stereotype.repository import Repository


def test_repository() -> None:
    @Repository()
    class SampleRepository: ...

    class NonAnnotated: ...

    assert Repository.single_or_none(SampleRepository) is not None
    assert Repository.single_or_none(NonAnnotated) is None
