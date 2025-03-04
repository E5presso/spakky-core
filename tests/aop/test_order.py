import pytest

from spakky.pod.annotations.order import Order


def test_order_cannot_be_negative() -> None:
    with pytest.raises(ValueError, match="Order cannot be negative"):
        Order(-1)
