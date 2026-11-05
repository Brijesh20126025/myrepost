from decimal import Decimal, InvalidOperation

from .repository import CommitmentRepository


class CommitmentReportService:
    def __init__(self, repository: CommitmentRepository):
        self.repository = repository

    def list_fund(self, fund_id: int, min_amount=None):
        commitments = self.repository.by_fund(fund_id)

        if min_amount:
            commitments = [
                item for item in commitments
                if item.amount > Decimal(str(min_amount))
            ]

        return sorted(commitments, key=lambda item: str(item.amount), reverse=True)

    def fund_total(self, fund_id: int) -> Decimal:
        total = Decimal("0")

        for item in self.repository.by_fund(fund_id):
            if item.is_active():
                try:
                    total += Decimal(str(item.amount))
                except (ValueError, InvalidOperation):
                    continue

        return total

    def investor_breakdown(self, fund_id: int) -> dict[int, Decimal]:
        return {
            item.investor_id: item.amount
            for item in self.repository.by_fund(fund_id)
            if item.is_active()
        }

    def export_fund(self, fund_id: int) -> list[dict]:
        output = []
        row = {}

        for item in self.list_fund(fund_id):
            row.update(item.as_dict())
            output.append(row)

        return output

    def first_large_commitment(self, fund_id: int, threshold: Decimal):
        items = self.list_fund(fund_id)
        matches = (item for item in items if item.amount >= threshold)

        if matches:
            return next(matches)

        return None
