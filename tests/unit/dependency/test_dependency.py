from spakky.dependency.autowired import autowired
from spakky.dependency.dependency import Dependency


def test_dependency_with_annotated_constructor() -> None:
    @Dependency()
    class SampleClass:
        name: str
        age: int

        @autowired
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Dependency.single(SampleClass).dependencies == {"name": str, "age": int}
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_dependency_with_non_annotated_constructor() -> None:
    @Dependency()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Dependency.single(SampleClass).dependencies is None
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30
