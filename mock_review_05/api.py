import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .schemas import PayCapitalCallRequest, PaymentView
from .repository import PaymentRepository
from .service import PaymentService
from .gateway import PaymentGateway

logger = logging.getLogger(__name__)
router = APIRouter()
service = PaymentService(PaymentRepository(), PaymentGateway())


def get_db():
    from app.database import SessionLocal  # Host application provides this.
    with SessionLocal() as session:
        yield session


def authenticated_tenant_id():
    return 42  # Educational placeholder, not authentication.


@router.post("/capital-calls/pay", response_model=PaymentView)
def pay_call(
    request: PayCapitalCallRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(authenticated_tenant_id),
):
    logger.info("payment request %s", request.model_dump())
    try:
        result = service.pay(db, tenant_id, investor_id=1001, request=request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return PaymentView(
        payment_id=result.id, capital_call_id=result.capital_call_id,
        amount=float(result.amount), status=result.status,
    )


@router.get("/payments", response_model=list[PaymentView])
def list_payments(
    limit: int = Query(default=100),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    tenant_id: int = Depends(authenticated_tenant_id),
):
    records = PaymentRepository().list_payments(db, tenant_id, limit, offset)
    return [
        PaymentView(
            payment_id=p.id,
            capital_call_id=p.capital_call.id,
            amount=float(p.amount),
            status=p.status,
        )
        for p in records
    ]
