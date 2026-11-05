import pytest

from mock_review_01.repository import InvestorRepository
from mock_review_01.service import InvestorService


@pytest.fixture
def service():
    return InvestorService(InvestorRepository())


def test_register_investor(service):
    investor = service.register(1, "Alice Smith", "alice@example.com")
    assert investor.id == 1
    assert investor.email == "alice@example.com"


def test_duplicate_email_rejected(service):
    service.register(1, "Alice", "alice@example.com")
    with pytest.raises(ValueError):
        service.register(2, "Another Alice", "ALICE@example.com")


def test_deactivate_investor(service):
    service.register(3, "Bob", "bob@example.com")
    assert service.deactivate(3) is True
    assert service.repository.find_by_id(3).active is False


def test_summary(service):
    service.register(4, "  carol jones  ", "carol@example.com", ["vip"])
    summary = service.get_summary(4)
    assert summary["name"] == "Carol Jones"
    assert summary["tags"] == ["vip"]
