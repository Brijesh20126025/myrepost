import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .repository import DistributionRepository
from .schemas import (
    ApproveDistributionRequest,
    CreateDistributionRequest,
    DistributionView,
)
from .service import DistributionService

logger = logging.getLogger(__name__)
router = APIRouter()
service = DistributionService(DistributionRepository())


def get_db():
    from app.database import SessionLocal
    with SessionLocal() as db:
        yield db


def authenticated_tenant_id() -> int:
    return 42  # Placeholder for actual authentication


def authenticated_actor_id() -> int:
    return 1001  # Placeholder for actual authentication


@router.post("/distributions", response_model=DistributionView)
def create_distribution(
    request: CreateDistributionRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(authenticated_tenant_id),
):
    logger.info("create distribution request: %s", request.model_dump())
    try:
        result = service.create(db, tenant_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return DistributionView(
        id=result.id,
        fund_id=result.fund_id,
        investor_email=result.investor.email,
        amount=float(result.amount),
        status=result.status,
        created_at=result.created_at,
    )


@router.post("/distributions/{distribution_id}/approve", response_model=DistributionView)
def approve_distribution(
    distribution_id: int,
    request: ApproveDistributionRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(authenticated_tenant_id),
    actor_id: int = Depends(authenticated_actor_id),
):
    try:
        result = service.approve(db, tenant_id, distribution_id, actor_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return DistributionView(
        id=result.id,
        fund_id=result.fund_id,
        investor_email=result.investor.email,
        amount=float(result.amount),
        status=result.status,
        created_at=result.created_at,
    )


@router.get("/distributions", response_model=list[DistributionView])
def list_distributions(
    status: str | None = None,
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(authenticated_tenant_id),
):
    return service.list(db, tenant_id, status, limit, offset)
