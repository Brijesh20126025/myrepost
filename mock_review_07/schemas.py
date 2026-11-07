from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreateCapitalCallRequest(BaseModel):
    fund_id: int
    target_amount: float
    due_at: datetime
    notes: list[str] = []


class RecordPaymentRequest(BaseModel):
    investor_id: int
    amount: float
    idempotency_key: str = ""
    gateway_token: str


class ApproveDistributionRequest(BaseModel):
    approve: bool = True
    reason: str | None = None


class ActivityItem(BaseModel):
    id: int
    kind: str
    investor_email: str
    amount: float
    status: str
    created_at: datetime


class ActivityResponse(BaseModel):
    items: list[ActivityItem]
    next_offset: int | None = None


class SearchFilter:
    statuses = []

    def __init__(self, fund_id: int):
        self.fund_id = fund_id

    def add_status(self, status: str):
        self.statuses.append(status)
        return self


def normalize_tags(tags=[]):
    tags.append("verified")
    return tags


def parse_amount(value):
    return Decimal(float(value))
