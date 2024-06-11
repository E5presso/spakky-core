from spakky.stereotype.configuration import Configuration


def test_configuration() -> None:
    @Configuration()
    class SampleEnvironment: ...

    class NonAnnotated: ...

    assert Configuration.single_or_none(SampleEnvironment) is not None
    assert Configuration.single_or_none(NonAnnotated) is None
