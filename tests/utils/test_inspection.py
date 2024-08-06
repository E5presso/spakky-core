from typing import Protocol

from spakky.utils.inspection import has_default_constructor, is_instance_method


def test_is_instance_method() -> None:
    def func() -> str:
        return "Hello, World!"

    class A:
        def method(self) -> str:
            return "Hello, World!"

    assert is_instance_method(A().method) is True
    assert is_instance_method(func) is False


def test_has_default_constructor() -> None:
    class A:
        def __init__(self) -> None:
            pass

    class B:
        pass

    assert has_default_constructor(A) is False
    assert has_default_constructor(B) is True


def test_has_default_constructor_with_protocol() -> None:
    class A:
        def __init__(self) -> None:
            pass

    class B(Protocol):
        pass

    assert has_default_constructor(A) is False
    assert has_default_constructor(B) is True
