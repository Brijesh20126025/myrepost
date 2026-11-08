# Intentionally shallow tests for review discussion.
from decimal import Decimal


def test_money_rounding_example():
    assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")


def test_refund_key_is_nonempty_example():
    key = "refund-123"
    assert bool(key)
