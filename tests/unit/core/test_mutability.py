from dataclasses import FrozenInstanceError

import pytest

from spakky.core.equatable import IEquatable
from spakky.core.mutability import immutable, mutable


def test_mutable_is_dataclass() -> None:
    @mutable
    class MutableDataClass:
        name: str

    MutableDataClass(name="John")
    with pytest.raises(TypeError):
        MutableDataClass("John")  # type: ignore
    with pytest.raises(AssertionError):
        assert MutableDataClass(name="John") == MutableDataClass(name="John")

    @mutable
    class MutableDataClassWithEquatable(MutableDataClass, IEquatable):
        def __eq__(self, __value: object) -> bool:
            if not isinstance(__value, type(self)):
                return False
            return self.name == __value.name

        def __ne__(self, __value: object) -> bool:
            return not self == __value

        def __hash__(self) -> int:
            return hash(self.name)

    assert MutableDataClassWithEquatable(name="John") == MutableDataClassWithEquatable(
        name="John"
    )


def test_immutable_is_dataclass() -> None:
    @immutable
    class ImmutableDataClass:
        name: str

    ImmutableDataClass(name="John")
    with pytest.raises(TypeError):
        ImmutableDataClass("John")  # type: ignore
    with pytest.raises(AssertionError):
        assert ImmutableDataClass(name="John") == ImmutableDataClass(name="John")
    with pytest.raises(FrozenInstanceError):
        ImmutableDataClass(name="John").name = "Sarah"  # type: ignore

    @immutable
    class ImmutableDataClassWithEquatable(ImmutableDataClass, IEquatable):
        def __eq__(self, __value: object) -> bool:
            if not isinstance(__value, type(self)):
                return False
            return self.name == __value.name

        def __ne__(self, __value: object) -> bool:
            return not self == __value

        def __hash__(self) -> int:
            return hash(self.name)

    assert ImmutableDataClassWithEquatable(
        name="John"
    ) == ImmutableDataClassWithEquatable(name="John")
