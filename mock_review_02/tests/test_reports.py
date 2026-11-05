from decimal import Decimal

import pytest

from mock_review_02.models import Commitment
from mock_review_02.repository import CommitmentRepository
from mock_review_02.service import CommitmentReportService


@pytest.fixture
def service():
    repository = CommitmentRepository()
    repository.add(Commitment(1, 10, 101, Decimal("100.00")))
    repository.add(Commitment(2, 10, 102, Decimal("50.00")))
    repository.add(Commitment(3, 20, 103, Decimal("30.00")))
    return CommitmentReportService(repository)


def test_fund_total(service):
    assert service.fund_total(10) == Decimal("150.00")


def test_list_fund(service):
    items = service.list_fund(10)
    assert len(items) == 2
    assert {item.id for item in items} == {1, 2}


def test_min_amount(service):
    items = service.list_fund(10, min_amount=Decimal("40.00"))
    assert {item.id for item in items} == {1, 2}


def test_investor_breakdown(service):
    breakdown = service.investor_breakdown(10)
    assert breakdown[101] == Decimal("100.00")
    assert breakdown[102] == Decimal("50.00")


def test_export_fund(service):
    rows = service.export_fund(10)
    assert len(rows) == 2
    assert all("investor_id" in row for row in rows)
