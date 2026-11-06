from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import WithdrawalRequest, WithdrawalResponse
from .service import WithdrawalService
from .repository import WithdrawalRepository

router = APIRouter()
service = WithdrawalService(WithdrawalRepository())


def get_db():
    from app.database import SessionLocal  # Provided by the host application
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def current_tenant_id():
    return 42  # Placeholder for an authenticated tenant dependency


@router.post("/withdrawals", response_model=WithdrawalResponse)
def create_withdrawal(
    request: WithdrawalRequest,
    db: Session = Depends(get_db),
    tenant_id: int = Depends(current_tenant_id),
):
    try:
        result = service.withdraw(db, tenant_id, request)
        return WithdrawalResponse(
            withdrawal_id=result.id,
            amount=result.amount,
            status=result.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
