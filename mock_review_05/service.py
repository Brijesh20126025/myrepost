import json
from decimal import Decimal

from .models import LedgerEntry, OutboxEvent, Payment
from .repository import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository, gateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, db, tenant_id: int, investor_id: int, request):
        existing = self.repository.find_by_key(db, request.idempotency_key)
        if existing:
            return existing

        call = self.repository.find_call(db, request.capital_call_id)
        if call is None:
            raise ValueError("Capital call not found")

        amount = Decimal(request.amount)
        remaining = call.requested_amount - call.collected_amount
        if amount > remaining:
            raise ValueError("Amount exceeds remaining balance")

        reference = self.gateway.charge(
            investor_id, amount, request.idempotency_key
        )

        call.collected_amount += amount
        payment = Payment(
            tenant_id=tenant_id,
            capital_call_id=call.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
            gateway_reference=reference,
        )
        db.add(payment)
        db.flush()

        db.add(LedgerEntry(
            payment_id=payment.id, account="CASH",
            direction="DEBIT", amount=amount,
        ))
        db.commit()

        db.add(LedgerEntry(
            payment_id=payment.id, account="CAPITAL_RECEIVABLE",
            direction="CREDIT", amount=amount,
        ))
        db.add(OutboxEvent(
            payment_id=payment.id,
            event_type="PAYMENT_COMPLETED",
            payload=json.dumps({"payment_id": payment.id, "tenant_id": tenant_id}),
        ))
        db.commit()
        return payment
