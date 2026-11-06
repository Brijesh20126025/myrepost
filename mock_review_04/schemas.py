from decimal import Decimal
from pydantic import BaseModel


class WithdrawalRequest(BaseModel):
    investor_id: int
    amount: float
    idempotency_key: str


class WithdrawalResponse(BaseModel):
    withdrawal_id: int
    amount: Decimal
    status: str
