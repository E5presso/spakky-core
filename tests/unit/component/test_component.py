from spakky.component.component import Component


def test_component() -> None:
    @Component()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Component.single(SampleClass).dependencies == {"name": str, "age": int}
    assert Component.single(SampleClass).name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30
