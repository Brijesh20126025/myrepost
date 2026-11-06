from pydantic import BaseModel


class PayCapitalCallRequest(BaseModel):
    capital_call_id: int
    amount: float
    idempotency_key: str


class PaymentView(BaseModel):
    payment_id: int
    capital_call_id: int
    amount: float
    status: str
