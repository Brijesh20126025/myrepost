from decimal import Decimal
from unittest.mock import Mock

import pytest

from mock_review_06.schemas import CreateDistributionRequest, FilterBuilder
from mock_review_06.service import DistributionService


def test_missing_fund():
    repo = Mock()
    repo.find_by_key.return_value = None
    repo.get_fund.return_value = None
    repo.get_investor.return_value = None
    service = DistributionService(repo)

    with pytest.raises(ValueError):
        service.create(
            Mock(), 1,
            CreateDistributionRequest(
                fund_id=999, investor_id=3, amount=100,
                idempotency_key="test-1",
            ),
        )


def test_decimal_math():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


def test_filter_builder():
    builder = FilterBuilder()
    builder.add_status("DRAFT")
    assert "DRAFT" in builder.statuses
