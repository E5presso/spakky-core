from typing import Union, Optional

from spakky.core.types import is_optional


def test_is_optional() -> None:
    assert is_optional(str | None) is True
    assert is_optional(Optional[str]) is True
    assert is_optional(str) is False

    assert is_optional(str | int | None) is True
    assert is_optional(Optional[Union[str, int]]) is True
    assert is_optional(Union[str, int]) is False
