import pytest

from spakky.bean.autowired import (
    Autowired,
    CannotAutowiringNonConstructorMethodError,
    Unknown,
    autowired,
)


def test_autowired_with_full_annotations() -> None:
    class Sample:
        @autowired
        def __init__(self, name: str, age: int) -> None:
            self.name: str = name
            self.age: int = age

    assert Autowired.single(Sample.__init__).dependencies == {"name": str, "age": int}


def test_autowired_with_partial_annotations() -> None:
    class Sample:
        @autowired
        def __init__(self, name: str, age) -> None:  # type: ignore
            self.name: str = name
            self.age: int = age

    assert Autowired.single(Sample.__init__).dependencies == {"name": str, "age": Unknown}  # type: ignore


def test_autowired_expect_raise_error() -> None:
    with pytest.raises(CannotAutowiringNonConstructorMethodError):

        class _:
            @autowired
            def just_method(self, name: str, age) -> None:  # type: ignore
                self.name: str = name
                self.age: int = age
