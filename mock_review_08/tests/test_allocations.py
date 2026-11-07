from decimal import Decimal

import pytest

from mock_review_08.allocations import AllocationBook, normalize_tags


def test_register_and_allocate():
    book = AllocationBook("Fund A", "1000.00")
    book.register(1, "Alex")
    assert book.allocate(1, "100.00") == Decimal("100.00")


def test_total_single_allocation():
    book = AllocationBook("Fund B", "1000.00")
    book.register(2, "Sam")
    book.allocate(2, "25.00")
    assert book.total_allocated() == Decimal("25.00")


def test_normalize_tags():
    assert "active" in normalize_tags()


def test_unknown_investor_rejected_on_allocate():
    book = AllocationBook("Fund C", "500.00")
    with pytest.raises(ValueError):
        book.allocate(999, "10.00")
