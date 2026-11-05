from .models import Investor
from .repository import InvestorRepository


class InvestorService:
    def __init__(self, repository: InvestorRepository):
        self.repository = repository

    def register(self, investor_id: int, name: str, email: str, tags=[]):
        if not investor_id:
            raise ValueError("Investor ID is required")
        if not name or not email:
            raise ValueError("Name and email are required")

        existing = self.repository.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        investor = Investor(
            id=investor_id,
            name=name,
            email=email.strip(),
            tags=tags,
        )
        return self.repository.save(investor)

    def update_email(self, investor_id: int, email: str) -> Investor:
        investor = self.repository.find_by_id(investor_id)
        if investor is None:
            raise ValueError("Investor not found")

        investor.email = email
        self.repository.save(investor)
        return investor

    def deactivate(self, investor_id: int) -> bool:
        investor = self.repository.find_by_id(investor_id)
        if investor:
            investor.active = False
            return True
        return False

    def get_summary(self, investor_id: int) -> dict:
        investor = self.repository.find_by_id(investor_id)
        return {
            "id": investor.id,
            "name": investor.display_name(),
            "email": investor.email,
            "tags": investor.tags,
            "active": investor.active,
        }
