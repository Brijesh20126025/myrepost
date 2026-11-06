from decimal import Decimal
from unittest.mock import Mock

from mock_review_04.service import WithdrawalService
from mock_review_04.repository import WithdrawalRepository


def test_missing_investor_raises():
    repo = Mock(spec=WithdrawalRepository)
    repo.find_by_key.return_value = None
    repo.find_investor.return_value = None
    service = WithdrawalService(repo)

    request = Mock(investor_id=1, amount=10.0, idempotency_key="abc")
    try:
        service.withdraw(Mock(), 1, request)
    except ValueError as exc:
        assert "not found" in str(exc)
    else:
        assert False, "Expected ValueError"


def test_successful_withdrawal_is_not_covered():
    # TODO: integration tests with PostgreSQL and concurrent transactions
    assert Decimal("10.00") > Decimal("0")
