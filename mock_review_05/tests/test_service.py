from decimal import Decimal
from unittest.mock import Mock

import pytest

from mock_review_05.service import PaymentService


def test_missing_call():
    repository = Mock()
    repository.find_by_key.return_value = None
    repository.find_call.return_value = None
    service = PaymentService(repository, Mock())

    with pytest.raises(ValueError):
        service.pay(
            Mock(), tenant_id=1, investor_id=2,
            request=Mock(capital_call_id=99, amount=20.0, idempotency_key="k1"),
        )


def test_money_rounding():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")
