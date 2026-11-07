import json
from decimal import Decimal

from sqlalchemy import select

from .models import Distribution, Fund, LedgerEntry, OutboxEvent
from .repositories import DistributionRepository


class DistributionService:
    def __init__(self):
        self.distributions = DistributionRepository()

    def approve(self, db, tenant_id: int, actor_id: int, distribution_id: int, request):
        distribution = self.distributions.get(db, distribution_id)
        if distribution is None:
            raise ValueError("Distribution not found")

        if distribution.status == "APPROVED":
            return distribution

        if not request.approve:
            distribution.status = "REJECTED"
            db.commit()
            return distribution

        fund = db.scalar(
            select(Fund).where(Fund.id == distribution.fund_id)
        )
        if fund.available_cash < distribution.amount:
            raise ValueError("Insufficient cash")

        fund.available_cash -= distribution.amount
        distribution.status = "APPROVED"
        distribution.approved_by = actor_id

        db.add(LedgerEntry(
            tenant_id=tenant_id,
            reference_type="DISTRIBUTION",
            reference_id=distribution.id,
            account="DISTRIBUTION_PAYABLE",
            direction="DEBIT",
            amount=distribution.amount,
        ))
        db.commit()

        db.add(LedgerEntry(
            tenant_id=tenant_id,
            reference_type="DISTRIBUTION",
            reference_id=distribution.id,
            account="FUND_CASH",
            direction="CREDIT",
            amount=distribution.amount,
        ))
        db.add(OutboxEvent(
            tenant_id=tenant_id,
            event_type="DISTRIBUTION_APPROVED",
            aggregate_id=distribution.id,
            payload=json.dumps({
                "distribution_id": distribution.id,
                "investor_id": distribution.investor_id,
                "amount": float(distribution.amount),
            }),
        ))
        db.commit()
        return distribution
