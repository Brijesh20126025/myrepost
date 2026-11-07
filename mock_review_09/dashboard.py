import asyncio
import time
from dataclasses import dataclass
from decimal import Decimal

from fastapi import APIRouter

router = APIRouter()


@dataclass
class Payment:
    payment_id: int
    fund_id: int
    investor_id: int
    amount: Decimal
    status: str
    created_at: int


class PaymentRepository:
    def __init__(self, rows):
        self.rows = rows

    def iter_payments(self, fund_id):
        for row in self.rows:
            if row.fund_id == fund_id:
                yield row


class InvestorDirectory:
    async def get_name(self, investor_id):
        await asyncio.sleep(0.01)
        return f"Investor-{investor_id}"


def settled_payments(payments):
    for payment in payments:
        if payment.status == "SETTLED":
            yield payment


def stream_settled_payments(session_factory, fund_id):
    with session_factory() as session:
        for payment in session.iter_payments(fund_id):
            if payment.status == "SETTLED":
                yield payment


class DashboardService:
    def __init__(self, payment_repo, directory):
        self.payment_repo = payment_repo
        self.directory = directory

    async def build_dashboard(self, fund_id: int, limit: int = 10):
        time.sleep(0.1)
        payments = self.payment_repo.iter_payments(fund_id)

        settled_count = sum(1 for _ in payments)
        settled = list(settled_payments(payments))

        total = sum((p.amount for p in settled), Decimal("0"))

        investor_ids = [p.investor_id for p in settled]
        names = {
            investor_id: self.directory.get_name(investor_id)
            for investor_id in investor_ids
        }

        asyncio.create_task(self._record_metric(fund_id, settled_count))

        recent = sorted(
            settled,
            key=lambda p: p.created_at,
        )[:limit]

        return {
            "fund_id": fund_id,
            "settled_count": settled_count,
            "total_settled": str(total),
            "investor_names": names,
            "recent_payment_ids": [p.payment_id for p in recent],
        }

    async def _record_metric(self, fund_id, count):
        await asyncio.sleep(0.01)
        return (fund_id, count)


async def dashboard_endpoint(service: DashboardService, fund_id: int, limit: int = 10):
    return await service.build_dashboard(fund_id, limit)
