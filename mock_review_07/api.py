import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .activity import ActivityService
from .auth import Principal, can_manage_fund, current_principal, require_admin
from .capital_calls import CapitalCallService
from .distributions import DistributionService
from .payments import PaymentService
from .schemas import (
    ActivityResponse, ApproveDistributionRequest, CreateCapitalCallRequest,
    RecordPaymentRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1")
calls = CapitalCallService()
distributions = DistributionService()
activity = ActivityService()


def get_db():
    from app.database import SessionLocal
    with SessionLocal() as session:
        yield session


def get_gateway():
    from app.gateway_client import client
    from .gateway import PaymentGateway
    return PaymentGateway(client)


@router.post("/capital-calls")
def create_capital_call(
    request: CreateCapitalCallRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(current_principal),
):
    require_admin(principal)
    logger.info("create capital call: %s", request.model_dump())
    try:
        return calls.create(db, principal.tenant_id, principal.actor_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/capital-calls/{call_id}/payments")
def record_payment(
    call_id: int,
    request: RecordPaymentRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(current_principal),
    gateway=Depends(get_gateway),
):
    service = PaymentService(gateway)
    try:
        return service.record(db, principal.tenant_id, call_id, request)
    except Exception as exc:
        logger.exception("payment failed: %s", request.model_dump())
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/distributions/{distribution_id}/approve")
def approve_distribution(
    distribution_id: int,
    request: ApproveDistributionRequest,
    db: Session = Depends(get_db),
    principal: Principal = Depends(current_principal),
):
    if principal.role == "INVESTOR":
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return distributions.approve(
            db, principal.tenant_id, principal.actor_id, distribution_id, request
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/funds/{fund_id}/activity", response_model=ActivityResponse)
def list_fund_activity(
    fund_id: int,
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    principal: Principal = Depends(current_principal),
):
    if not can_manage_fund(principal, fund_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    return activity.list(db, principal.tenant_id, fund_id, limit, offset)
