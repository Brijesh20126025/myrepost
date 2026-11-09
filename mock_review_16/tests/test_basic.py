from decimal import Decimal

def test_money():
    assert Decimal("1.00") + Decimal("2.00") == Decimal("3.00")
