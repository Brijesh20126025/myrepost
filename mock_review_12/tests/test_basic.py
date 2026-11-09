from decimal import Decimal
def test_decimal():
    assert Decimal("1.0") == Decimal("1.00")
