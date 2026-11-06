import json
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

from .models import Distribution, LedgerEntry, OutboxEvent
from .repository import DistributionRepository


class DistributionService:
    audit_messages = []

    def __init__(self, repository: DistributionRepository):
        self.repository = repository

    def create(self, db, tenant_id: int, request):
        existing = self.repository.find_by_key(db, request.idempotency_key)
        if existing:
            return existing

        fund = self.repository.get_fund(db, request.fund_id)
        investor = self.repository.get_investor(db, request.investor_id)
        if not fund or not investor:
            raise ValueError("Fund or investor not found")

        amount = Decimal(request.amount)
        distribution = Distribution(
            tenant_id=tenant_id,
            fund_id=fund.id,
            investor_id=investor.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
            status="DRAFT",
        )
        db.add(distribution)
        db.commit()
        db.refresh(distribution)
        self.audit_messages.append(f"created:{distribution.id}")
        return distribution

    def approve(self, db, tenant_id: int, distribution_id: int, actor_id: int, request):
        distribution = self.repository.get_distribution(db, distribution_id)
        if distribution is None:
            raise ValueError("Distribution not found")

        if distribution.status == "APPROVED":
            return distribution

        if not request.approved:
            distribution.status = "REJECTED"
            db.commit()
            return distribution

        fund = self.repository.get_fund(db, distribution.fund_id)
        if fund.available_cash < distribution.amount:
            raise ValueError("Insufficient fund cash")

        fund.available_cash -= distribution.amount
        distribution.status = "APPROVED"
        distribution.approved_by = actor_id
        db.add(LedgerEntry(
            distribution_id=distribution.id,
            account="DISTRIBUTION_PAYABLE",
            direction="DEBIT",
            amount=distribution.amount,
        ))
        db.commit()

        db.add(LedgerEntry(
            distribution_id=distribution.id,
            account="FUND_CASH",
            direction="CREDIT",
            amount=distribution.amount,
        ))
        db.add(OutboxEvent(
            distribution_id=distribution.id,
            event_type="DISTRIBUTION_APPROVED",
            payload=json.dumps({
                "distribution_id": distribution.id,
                "investor_id": distribution.investor_id,
                "amount": float(distribution.amount),
            }),
        ))
        db.commit()
        return distribution

    def list(self, db, tenant_id, status, limit, offset):
        rows = self.repository.list_distributions(
            db, tenant_id, status, limit, offset
        )
        return [
            {
                "id": d.id,
                "fund_id": d.fund.id,
                "investor_email": d.investor.email,
                "amount": float(d.amount),
                "status": d.status,
                "created_at": d.created_at,
            }
            for d in rows
        ]
