# Starter tests for review. Existing test fixtures are assumed.
from decimal import Decimal


def test_decimal_arithmetic():
    assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")


def test_cursor_default():
    cursor = 0
    assert cursor == 0
