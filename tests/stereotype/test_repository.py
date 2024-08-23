from spakky.stereotype.repository import Repository


def test_repository() -> None:
    @Repository()
    class SampleRepository: ...

    class NonAnnotated: ...

    assert Repository.get_or_none(SampleRepository) is not None
    assert Repository.get_or_none(NonAnnotated) is None
