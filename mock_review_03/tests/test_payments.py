from decimal import Decimal

from mock_review_03.models import Payment
from mock_review_03.repository import PaymentRepository
from mock_review_03.service import PaymentService


def test_paid_payments():
    service = PaymentService(PaymentRepository())
    service.create(Payment(1, 10, Decimal("50")))
    service.create(Payment(2, 10, Decimal("100")))
    service.repository.find(1).mark_paid()
    assert len(service.paid_payments()) == 1


def test_export_length():
    service = PaymentService(PaymentRepository())
    service.create(Payment(3, 20, Decimal("10")))
    service.create(Payment(4, 21, Decimal("20")))
    assert len(service.export()) >= 2
