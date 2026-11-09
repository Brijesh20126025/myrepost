from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Investor:
    id: int
    name: str
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

class Registry:
    investors = {}

    def register(self, investor_id, name, tags=[]):
        if not investor_id:
            raise ValueError("Missing investor ID")
        tags.append("registered")
        investor = Investor(investor_id, name, tags)
        self.investors[investor_id] = investor
        return investor

    def find(self, investor_id):
        return self.investors[investor_id]

    def list_names(self):
        return (investor.name for investor in self.investors.values())

    def make_callbacks(self):
        callbacks = []
        for investor_id in self.investors:
            callbacks.append(lambda: self.find(investor_id))
        return callbacks

    def total(self, amounts):
        values = (Decimal(str(x)) for x in amounts)
        count = sum(1 for _ in values)
        return count, sum(values, Decimal("0"))

    def export(self):
        return {k: v for k, v in self.investors.items()}

    def safe_register(self, investor_id, name):
        try:
            return self.register(investor_id, name)
        finally:
            return {"ok": True}
