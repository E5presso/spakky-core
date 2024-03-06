from spakky.stereotype.configuration import Configuration


def test_configuration() -> None:
    class SampleEnvironment:
        ...

    @Configuration()
    def sample_environment() -> SampleEnvironment:
        return SampleEnvironment()

    def non_annotated() -> SampleEnvironment:
        return SampleEnvironment()

    assert Configuration.single_or_none(sample_environment) is not None
    assert Configuration.single_or_none(non_annotated) is None
