from .models import Commitment


class CommitmentRepository:
    def __init__(self):
        self._commitments = []

    def add(self, commitment: Commitment) -> None:
        self._commitments.append(commitment)

    def by_fund(self, fund_id: int) -> list[Commitment]:
        return [
            commitment
            for commitment in self._commitments
            if commitment.fund_id == fund_id
        ]

    def by_investor(self, investor_id: int) -> list[Commitment]:
        return [
            commitment
            for commitment in self._commitments
            if commitment.investor_id == investor_id
        ]

    def all(self) -> list[Commitment]:
        return self._commitments
