from sqlalchemy import select

from .models import CapitalCall, Distribution, Fund, FundMembership, Investor, Payment


class FundRepository:
    def get(self, db, fund_id: int):
        return db.get(Fund, fund_id)

    def find_membership(self, db, tenant_id: int, fund_id: int, actor_id: int):
        return db.scalar(
            select(FundMembership).where(
                FundMembership.tenant_id == tenant_id,
                FundMembership.fund_id == fund_id,
                FundMembership.actor_id == actor_id,
            )
        )


class CapitalCallRepository:
    def get(self, db, call_id: int):
        return db.get(CapitalCall, call_id)

    def list_by_fund(self, db, fund_id: int):
        return db.scalars(
            select(CapitalCall).where(CapitalCall.fund_id == fund_id)
        ).all()


class PaymentRepository:
    def find_by_idempotency_key(self, db, key: str):
        return db.scalar(select(Payment).where(Payment.idempotency_key == key))

    def find_by_gateway_reference(self, db, reference: str):
        return db.scalar(select(Payment).where(Payment.gateway_reference == reference))

    def list_by_fund(self, db, tenant_id: int, fund_id: int, limit: int, offset: int):
        return db.scalars(
            select(Payment)
            .join(CapitalCall, Payment.capital_call_id == CapitalCall.id)
            .where(
                Payment.tenant_id == tenant_id,
                CapitalCall.fund_id == fund_id,
            )
            .order_by(Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()


class DistributionRepository:
    def get(self, db, distribution_id: int):
        return db.get(Distribution, distribution_id)

    def list_by_fund(self, db, tenant_id: int, fund_id: int, limit: int, offset: int):
        return db.scalars(
            select(Distribution)
            .where(
                Distribution.tenant_id == tenant_id,
                Distribution.fund_id == fund_id,
            )
            .order_by(Distribution.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()


class InvestorRepository:
    def get(self, db, investor_id: int):
        return db.get(Investor, investor_id)
