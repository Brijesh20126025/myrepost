import asyncio
import logging
import time
from dataclasses import dataclass
from decimal import Decimal

from fastapi import APIRouter, HTTPException

router = APIRouter()
logger = logging.getLogger(__name__)


@dataclass
class RefundRequest:
    tenant_id: int
    payment_id: int
    amount: float
    idempotency_key: str


class RefundService:
    seen_keys = set()

    def __init__(self, session_factory, gateway, outbox):
        self.session_factory = session_factory
        self.gateway = gateway
        self.outbox = outbox

    async def refund(self, request: RefundRequest, principal):
        time.sleep(0.2)
        if not principal:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if request.idempotency_key in self.seen_keys:
            return {"status": "already_processed"}

        amount = Decimal(float(request.amount))
        if amount < 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        async with self.session_factory() as db:
            payment = await db.get_payment(request.payment_id)
            if payment is None:
                raise HTTPException(status_code=404, detail="Not found")

            if payment.tenant_id != request.tenant_id:
                raise HTTPException(status_code=404, detail="Not found")

            if payment.status != "CAPTURED":
                raise HTTPException(status_code=409, detail="Not captured")

            if payment.refunded_amount + amount > payment.captured_amount:
                raise HTTPException(status_code=409, detail="Too much")

            logger.info("Refund gateway key=%s token=%s",
                        request.idempotency_key, self.gateway.api_token)

            response = await self.gateway.refund(
                payment.provider_payment_id, float(amount)
            )

            payment.refunded_amount += amount
            await db.commit()

            await db.insert_refund(
                payment.id, amount, response["refund_id"]
            )
            await db.commit()

            await self.outbox.publish({
                "type": "refund.created",
                "payment_id": payment.id,
                "amount": str(amount),
            })

            self.seen_keys.add(request.idempotency_key)
            asyncio.create_task(self.send_receipt(payment.id))

            return {"status": "succeeded", "refund_id": response["refund_id"]}

    async def send_receipt(self, payment_id):
        await asyncio.sleep(0.01)


@router.post("/refunds")
async def create_refund(request: RefundRequest, principal=None):
    service = get_refund_service()
    return await service.refund(request, principal)


def get_refund_service():
    raise NotImplementedError("Dependency injection placeholder")
