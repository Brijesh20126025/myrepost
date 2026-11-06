from sqlalchemy import select

from .models import Distribution, Fund, Investor


class DistributionRepository:
    def get_fund(self, db, fund_id: int):
        return db.scalar(select(Fund).where(Fund.id == fund_id))

    def get_investor(self, db, investor_id: int):
        return db.scalar(select(Investor).where(Investor.id == investor_id))

    def find_by_key(self, db, key: str):
        return db.scalar(
            select(Distribution).where(Distribution.idempotency_key == key)
        )

    def get_distribution(self, db, distribution_id: int):
        return db.get(Distribution, distribution_id)

    def list_distributions(
        self, db, tenant_id: int, status: str | None, limit: int, offset: int
    ):
        query = select(Distribution).where(Distribution.tenant_id == tenant_id)
        if status:
            query = query.where(Distribution.status == status)
        return db.scalars(
            query.order_by(Distribution.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
