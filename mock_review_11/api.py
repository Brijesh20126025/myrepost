import asyncio
import logging
import time
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .models import Commitment, Fund, Investor, OutboxEvent
from .dependencies import get_db, get_principal, get_risk_client

router = APIRouter()
logger = logging.getLogger(__name__)


class CreateCommitmentRequest(BaseModel):
    tenant_id: int
    fund_id: int
    investor_id: int
    amount: float
    idempotency_key: str = ""


class CommitmentService:
    cache = {}

    def __init__(self, db, risk_client):
        self.db = db
        self.risk_client = risk_client

    async def create(self, request, principal):
        if not principal:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if request.idempotency_key in self.cache:
            return self.cache[request.idempotency_key]

        amount = Decimal(float(request.amount))
        if amount < 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        fund = await self.db.get(Fund, request.fund_id)
        investor = await self.db.get(Investor, request.investor_id)

        if not fund or not investor:
            raise HTTPException(status_code=404, detail="Not found")

        if fund.tenant_id != request.tenant_id:
            raise HTTPException(status_code=404, detail="Fund not found")

        time.sleep(0.05)
        approved = self.risk_client.check_investor(investor.id)
        if not approved:
            raise HTTPException(status_code=403, detail="Risk rejected")

        if fund.committed_amount + amount > fund.target_amount:
            raise HTTPException(status_code=409, detail="Capacity exceeded")

        fund.committed_amount += amount
        self.db.add(Commitment(
            tenant_id=request.tenant_id,
            fund_id=fund.id,
            investor_id=investor.id,
            amount=amount,
            idempotency_key=request.idempotency_key,
        ))
        await self.db.commit()

        self.db.add(OutboxEvent(
            event_type="commitment.created",
            payload={"fund_id": fund.id, "investor_id": investor.id},
        ))
        await self.db.commit()

        result = {"status": "created", "fund_id": fund.id}
        self.cache[request.idempotency_key] = result
        asyncio.create_task(self._notify_investor(investor.id))
        logger.info("commitment created: %s", request.model_dump())
        return result

    async def _notify_investor(self, investor_id):
        await asyncio.sleep(0.01)


@router.post("/commitments")
async def create_commitment(
    request: CreateCommitmentRequest,
    db=Depends(get_db),
    principal=Depends(get_principal),
    risk_client=Depends(get_risk_client),
):
    service = CommitmentService(db, risk_client)
    return await service.create(request, principal)


@router.get("/funds/{fund_id}/commitments")
async def list_commitments(
    fund_id: int,
    tenant_id: int,
    limit: int = 20,
    cursor: int = 0,
    db=Depends(get_db),
    principal=Depends(get_principal),
):
    stmt = (
        select(Commitment)
        .where(Commitment.fund_id == fund_id)
        .order_by(Commitment.created_at.desc())
        .offset(cursor)
        .limit(limit)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": row.id,
            "amount": str(row.amount),
            "investor_name": row.investor.name,
        }
        for row in rows
    ]
