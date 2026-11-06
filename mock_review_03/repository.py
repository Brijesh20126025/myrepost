from .models import Payment


class PaymentRepository:
    payments = {}

    def add(self, payment: Payment):
        self.payments[payment.id] = payment

    def find(self, payment_id: int):
        return self.payments.get(payment_id)

    def all(self):
        return list(self.payments.values())
