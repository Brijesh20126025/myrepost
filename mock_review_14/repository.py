from sqlalchemy import select
from sqlalchemy.orm import joinedload
from .models import Fund, Commitment, Investor

class CommitmentRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, fund_id, investor_id, amount):
        fund = await self.db.get(Fund, fund_id)
        if fund.committed_amount + amount > fund.target_amount:
            raise ValueError("Capacity exceeded")
        fund.committed_amount += amount
        await self.db.commit()
        self.db.add(Commitment(
            fund_id=fund_id,
            investor_id=investor_id,
            amount=amount,
        ))
        await self.db.commit()
        return fund

    async def find_or_create_investor(self, email):
        result = await self.db.execute(
            select(Investor).where(Investor.email == email)
        )
        investor = result.scalar_one_or_none()
        if investor:
            return investor
        investor = Investor(email=email)
        self.db.add(investor)
        await self.db.flush()
        return investor

    async def list_funds(self):
        result = await self.db.execute(
            select(Fund).options(joinedload(Fund.commitments))
        )
        return result.scalars().all()

    async def list_commitments(self, fund_id, limit=20, offset=0):
        result = await self.db.execute(
            select(Commitment)
            .where(Commitment.fund_id == fund_id)
            .order_by(Commitment.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [
            {"id": c.id, "investor": c.investor.name}
            for c in result.scalars().all()
        ]
