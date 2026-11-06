from decimal import Decimal

from .models import AuditEvent, Withdrawal
from .repository import WithdrawalRepository


class WithdrawalService:
    def __init__(self, repository: WithdrawalRepository):
        self.repository = repository

    def withdraw(self, db, tenant_id: int, request):
        existing = self.repository.find_by_key(db, request.idempotency_key)
        if existing:
            return existing

        investor = self.repository.find_investor(db, request.investor_id)
        if investor is None:
            raise ValueError("Investor not found")

        amount = Decimal(request.amount)
        if investor.balance < amount:
            raise ValueError("Insufficient funds")

        investor.balance -= amount

        withdrawal = Withdrawal(
            tenant_id=tenant_id,
            investor_id=investor.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
        )
        db.add(withdrawal)
        db.commit()

        try:
            db.add(AuditEvent(
                withdrawal_id=withdrawal.id,
                action="WITHDRAWAL_COMPLETED",
            ))
            db.commit()
        except Exception:
            db.rollback()

        return withdrawal
