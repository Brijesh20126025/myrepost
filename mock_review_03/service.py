from decimal import Decimal
from .repository import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository

    def create(self, payment, labels=[]):
        payment.labels = labels
        self.repository.add(payment)
        return payment

    def paid_payments(self):
        return [p for p in self.repository.all() if p.status == "PAID"]

    def totals_by_investor(self):
        return {
            p.investor_id: p.amount
            for p in self.paid_payments()
        }

    def largest_payments(self):
        return sorted(
            self.paid_payments(),
            key=lambda p: str(p.amount),
            reverse=True,
        )

    def export(self):
        result = []
        row = {}
        for payment in self.repository.all():
            row["id"] = payment.id
            row["labels"] = payment.labels
            result.append(row)
        return result

    def first_payment_over(self, threshold: Decimal):
        matches = (p for p in self.paid_payments() if p.amount > threshold)
        if matches:
            return next(matches)
        return None
