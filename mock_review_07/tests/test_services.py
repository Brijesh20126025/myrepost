from decimal import Decimal
from unittest.mock import Mock

import pytest

from mock_review_07.schemas import (
    CreateCapitalCallRequest, RecordPaymentRequest, SearchFilter,
)
from mock_review_07.payments import PaymentService


def test_payment_missing_call():
    gateway = Mock()
    service = PaymentService(gateway)
    service.calls.get = Mock(return_value=None)
    service.investors.get = Mock(return_value=None)
    request = RecordPaymentRequest(
        investor_id=1, amount=100.0,
        idempotency_key="sample", gateway_token="tok_test",
    )
    with pytest.raises(ValueError):
        service.record(Mock(), 1, 99, request)


def test_money_arithmetic():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


def test_filter():
    filters = SearchFilter(fund_id=1)
    filters.add_status("SETTLED")
    assert "SETTLED" in filters.statuses


def test_gateway_not_called_on_missing_call():
    gateway = Mock()
    service = PaymentService(gateway)
    service.calls.get = Mock(return_value=None)
    service.investors.get = Mock(return_value=None)
    request = RecordPaymentRequest(
        investor_id=1, amount=100, idempotency_key="another",
        gateway_token="tok_test",
    )
    with pytest.raises(ValueError):
        service.record(Mock(), 1, 99, request)
    gateway.charge.assert_not_called()
