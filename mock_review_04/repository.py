from sqlalchemy import select

from .models import Investor, Withdrawal


class WithdrawalRepository:
    def find_investor(self, db, investor_id: int):
        return db.scalar(select(Investor).where(Investor.id == investor_id))

    def find_by_key(self, db, key: str):
        return db.scalar(
            select(Withdrawal).where(Withdrawal.idempotency_key == key)
        )

    def list_for_investor(self, db, investor_id: int):
        return db.scalars(
            select(Withdrawal).where(Withdrawal.investor_id == investor_id)
        ).all()
