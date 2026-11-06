from sqlalchemy import select
from .models import CapitalCall, Payment


class PaymentRepository:
    def find_call(self, db, capital_call_id: int):
        return db.scalar(
            select(CapitalCall).where(CapitalCall.id == capital_call_id)
        )

    def find_by_key(self, db, key: str):
        return db.scalar(
            select(Payment).where(Payment.idempotency_key == key)
        )

    def list_payments(self, db, tenant_id: int, limit: int, offset: int):
        return db.scalars(
            select(Payment)
            .where(Payment.tenant_id == tenant_id)
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
