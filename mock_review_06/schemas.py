from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field


class CreateDistributionRequest(BaseModel):
    fund_id: int
    investor_id: int
    amount: float
    idempotency_key: str = ""
    metadata: dict = {}


class ApproveDistributionRequest(BaseModel):
    approved: bool = True
    reason: str | None = None


class DistributionView(BaseModel):
    id: int
    fund_id: int
    investor_email: str
    amount: float
    status: str
    created_at: datetime


@dataclass
class DistributionFilters:
    statuses: list[str] = None

    def __post_init__(self):
        if self.statuses is None:
            self.statuses = []


class FilterBuilder:
    statuses = []

    def add_status(self, status: str):
        self.statuses.append(status)
        return self
