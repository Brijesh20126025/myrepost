import asyncio
from decimal import Decimal

from mock_review_09.dashboard import (
    DashboardService,
    InvestorDirectory,
    Payment,
    PaymentRepository,
)


def test_repository_filters_fund():
    repo = PaymentRepository([
        Payment(1, 10, 101, Decimal("5.00"), "SETTLED", 100),
        Payment(2, 20, 102, Decimal("7.00"), "SETTLED", 101),
    ])
    assert [p.payment_id for p in repo.iter_payments(10)] == [1]


def test_dashboard_smoke():
    repo = PaymentRepository([
        Payment(1, 10, 101, Decimal("5.00"), "SETTLED", 100),
    ])
    service = DashboardService(repo, InvestorDirectory())
    result = asyncio.run(service.build_dashboard(10))
    assert result["fund_id"] == 10
    assert result["settled_count"] == 1
