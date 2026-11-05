from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Commitment:
    id: int
    fund_id: int
    investor_id: int
    amount: Decimal
    status: str = "ACTIVE"

    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "fund_id": self.fund_id,
            "investor_id": self.investor_id,
            "amount": str(self.amount),
            "status": self.status,
        }
