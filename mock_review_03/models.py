from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Payment:
    id: int
    investor_id: int
    amount: Decimal
    status: str = "PENDING"
    labels: list[str] = field(default_factory=list)

    def mark_paid(self):
        self.status = "PAID"
