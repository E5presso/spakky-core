import pytest

from spakky.bean.autowired import autowired
from spakky.bean.bean import (
    Bean,
    BeanFactory,
    ReturnAnnotationNotFoundInBeanFactoryError,
)
from spakky.bean.provider import Provider, ProvidingType


def test_bean_with_autowired() -> None:
    @Bean()
    class SampleClass:
        name: str
        age: int

        @autowired
        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Bean.single(SampleClass).dependencies == {"name": str, "age": int}
    assert Bean.single(SampleClass).name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_bean_without_autowired() -> None:
    @Bean()
    class SampleClass:
        name: str
        age: int

        def __init__(self, name: str, age: int) -> None:
            self.name = name
            self.age = age

    assert Bean.single(SampleClass).dependencies == {}
    assert Bean.single(SampleClass).name == "sample_class"
    sample: SampleClass = SampleClass(name="John", age=30)
    assert sample.name == "John"
    assert sample.age == 30


def test_bean_with_return_annotation() -> None:
    class A:
        ...

    @BeanFactory()
    def get_a() -> A:
        return A()

    assert BeanFactory.contains(get_a) is True
    assert BeanFactory.single(get_a) is not None
    assert BeanFactory.single(get_a).name == "get_a"
    assert BeanFactory.single(get_a).bean_type is A
    assert BeanFactory.single(get_a).providing_type == ProvidingType.SINGLETON


def test_bean_without_return_annotation() -> None:
    class A:
        ...

    with pytest.raises(ReturnAnnotationNotFoundInBeanFactoryError):

        @BeanFactory()
        def _():
            return A()


def test_bean_with_provider() -> None:
    class A:
        ...

    @BeanFactory()
    @Provider(ProvidingType.FACTORY)
    def get_a() -> A:
        return A()

    assert BeanFactory.contains(get_a) is True
    assert BeanFactory.single(get_a) is not None
    assert BeanFactory.single(get_a).name == "get_a"
    assert BeanFactory.single(get_a).bean_type is A
    assert BeanFactory.single(get_a).providing_type == ProvidingType.FACTORY


def test_bean_without_provider() -> None:
    class A:
        ...

    @BeanFactory()
    def get_a() -> A:
        return A()

    assert BeanFactory.contains(get_a) is True
    assert BeanFactory.single(get_a) is not None
    assert BeanFactory.single(get_a).name == "get_a"
    assert BeanFactory.single(get_a).bean_type is A
    assert BeanFactory.single(get_a).providing_type == ProvidingType.SINGLETON
