import pytest

from spakky.bean.bean import Bean, CannotDetermineBeanTypeError


def test_bean() -> None:
    @Bean()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Bean.single(SampleClass).dependencies == {"name": str, "age": int}
    assert Bean.single(SampleClass).bean_name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_bean_factory_with_return_annotation() -> None:
    class A: ...

    @Bean()
    def get_a() -> A:
        return A()

    assert Bean.contains(get_a) is True
    assert Bean.single(get_a) is not None
    assert Bean.single(get_a).bean_name == "get_a"
    assert Bean.single(get_a).bean_type is A


def test_bean_factory_without_return_annotation() -> None:
    class A: ...

    with pytest.raises(CannotDetermineBeanTypeError):

        @Bean()
        def _():
            return A()


def test_bean_with_name() -> None:
    @Bean(bean_name="asdf")
    class A: ...

    assert Bean.contains(A) is True
    assert Bean.single(A) is not None
    assert Bean.single(A).bean_name == "asdf"


def test_bean_factory_with_name() -> None:
    class A: ...

    @Bean(bean_name="a")
    def get_a() -> A:
        return A()

    assert Bean.contains(get_a) is True
    assert Bean.single(get_a) is not None
    assert Bean.single(get_a).bean_name == "a"
    assert Bean.single(get_a).bean_type is A
