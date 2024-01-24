from spakky.stereotypes.environment import Environment


def test_environment() -> None:
    @Environment()
    class SampleEnvironment:
        ...

    class NonAnnotated:
        ...

    assert Environment.single_or_none(SampleEnvironment) is not None
    assert Environment.single_or_none(NonAnnotated) is None
