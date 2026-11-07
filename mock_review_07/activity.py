from .repositories import DistributionRepository, PaymentRepository


class ActivityService:
    def __init__(self):
        self.payments = PaymentRepository()
        self.distributions = DistributionRepository()

    def list(self, db, tenant_id: int, fund_id: int, limit: int, offset: int):
        payments = self.payments.list_by_fund(db, tenant_id, fund_id, limit, offset)
        distributions = self.distributions.list_by_fund(
            db, tenant_id, fund_id, limit, offset
        )
        rows = [
            {
                "id": p.id,
                "kind": "PAYMENT",
                "investor_email": p.investor.email,
                "amount": float(p.amount),
                "status": p.status,
                "created_at": p.created_at,
            }
            for p in payments
        ] + [
            {
                "id": d.id,
                "kind": "DISTRIBUTION",
                "investor_email": d.investor.email,
                "amount": float(d.amount),
                "status": d.status,
                "created_at": d.created_at,
            }
            for d in distributions
        ]
        rows.sort(key=lambda x: x["created_at"], reverse=True)
        return {"items": rows[:limit], "next_offset": offset + limit}
