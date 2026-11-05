from .models import Investor


class InvestorRepository:
    investors = {}

    def save(self, investor: Investor) -> Investor:
        self.investors[investor.id] = investor
        return investor

    def find_by_id(self, investor_id: int):
        return self.investors.get(investor_id)

    def find_by_email(self, email: str):
        for investor in self.investors.values():
            if investor.email.lower() == email.lower():
                return investor
        return None

    def list_active(self):
        return [investor for investor in self.investors.values() if investor.active]

    def delete(self, investor_id: int) -> bool:
        if investor_id in self.investors:
            del self.investors[investor_id]
            return True
        return False
