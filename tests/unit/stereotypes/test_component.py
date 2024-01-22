from spakky.stereotypes.component import Component


def test_component() -> None:
    @Component()
    class SampleComponent:
        ...

    class NonAnnotated:
        ...

    assert Component.single_or_none(SampleComponent) is not None
    assert Component.single_or_none(NonAnnotated) is None
