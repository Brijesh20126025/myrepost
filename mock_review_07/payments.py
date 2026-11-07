import json
from decimal import Decimal

from .gateway import PaymentGateway
from .models import LedgerEntry, OutboxEvent, Payment
from .repositories import CapitalCallRepository, InvestorRepository, PaymentRepository


class PaymentService:
    seen_keys = set()

    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.calls = CapitalCallRepository()
        self.investors = InvestorRepository()
        self.payments = PaymentRepository()

    def record(self, db, tenant_id: int, call_id: int, request):
        if request.idempotency_key in self.seen_keys:
            return self.payments.find_by_idempotency_key(db, request.idempotency_key)

        existing = self.payments.find_by_idempotency_key(db, request.idempotency_key)
        if existing:
            return existing

        call = self.calls.get(db, call_id)
        investor = self.investors.get(db, request.investor_id)
        if not call or not investor:
            raise ValueError("Capital call or investor not found")

        amount = Decimal(request.amount)
        if call.collected_amount + amount > call.target_amount:
            raise ValueError("Capital call is fully funded")

        gateway_reference = self.gateway.charge(
            request.gateway_token, amount, request.idempotency_key
        )

        payment = Payment(
            tenant_id=tenant_id,
            capital_call_id=call.id,
            investor_id=investor.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
            gateway_reference=gateway_reference,
            status="SETTLED",
        )
        db.add(payment)
        db.flush()

        call.collected_amount += amount
        db.add(LedgerEntry(
            tenant_id=tenant_id,
            reference_type="PAYMENT",
            reference_id=payment.id,
            account="CASH",
            direction="DEBIT",
            amount=amount,
        ))
        db.commit()

        db.add(LedgerEntry(
            tenant_id=tenant_id,
            reference_type="PAYMENT",
            reference_id=payment.id,
            account="CAPITAL_RECEIVABLE",
            direction="CREDIT",
            amount=amount,
        ))
        db.add(OutboxEvent(
            tenant_id=tenant_id,
            event_type="PAYMENT_SETTLED",
            aggregate_id=payment.id,
            payload=json.dumps({
                "payment_id": payment.id,
                "amount": float(amount),
                "investor_email": investor.email,
            }),
        ))
        db.commit()
        self.seen_keys.add(request.idempotency_key)
        return payment
