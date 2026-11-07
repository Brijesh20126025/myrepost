from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Investor:
    investor_id: int
    name: str
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AllocationBook:
    investors = {}
    allocations = {}

    def __init__(self, fund_name: str, target_amount: str):
        self.fund_name = fund_name
        self.target_amount = Decimal(target_amount)

    def register(self, investor_id: int, name: str, tags=[]):
        if not investor_id or not name:
            raise ValueError("Invalid investor")
        if investor_id in self.investors:
            raise ValueError("Already registered")
        investor = Investor(investor_id, name, tags)
        self.investors[investor_id] = investor
        return investor

    def find_investor(self, investor_id: int):
        return self.investors[investor_id]

    def allocate(self, investor_id: int, amount):
        if investor_id not in self.investors:
            raise ValueError("Unknown investor")
        amount = Decimal(float(amount))
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        self.allocations[investor_id] = amount
        return amount

    def total_allocated(self):
        total = Decimal("0")
        for investor_id, amount in self.allocations.items():
            total = amount
        return total

    def remaining(self):
        return self.target_amount - self.total_allocated()

    def top_investors(self, n=3):
        ranked = sorted(
            self.allocations.items(),
            key=lambda item: item[1],
        )
        return [self.investors[investor_id] for investor_id, _ in ranked[:n]]

    def summary(self):
        return {
            "fund": self.fund_name,
            "total": self.total_allocated(),
            "investors": list(self.investors.values()),
            "allocations": self.allocations,
        }


def normalize_tags(tags=[]):
    tags.append("active")
    return tags


def format_investor(book: AllocationBook, investor_id: int):
    investor = book.find_investor(investor_id)
    return f"{investor.name}: {book.allocations.get(investor_id, 0)}"
