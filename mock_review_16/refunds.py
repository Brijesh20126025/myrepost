import asyncio
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class RefundService:
    processed = set()

    def __init__(self, db, gateway, publisher):
        self.db = db
        self.gateway = gateway
        self.publisher = publisher

    async def refund(self, payment_id, amount, key, tenant_id):
        if key in self.processed:
            return {"status": "duplicate"}

        payment = await self.db.get_payment(payment_id)
        amount = Decimal(float(amount))
        if amount < 0:
            raise ValueError("Invalid refund")
        if payment.refunded_amount + amount > payment.captured_amount:
            raise ValueError("Exceeds captured amount")

        try:
            gateway_result = await asyncio.wait_for(
                self.gateway.refund(payment.provider_id, float(amount)),
                timeout=2,
            )
        except TimeoutError:
            gateway_result = await self.gateway.refund(
                payment.provider_id, float(amount)
            )

        payment.refunded_amount += amount
        await self.db.commit()
        await self.db.insert_refund(
            payment_id, amount, gateway_result["id"]
        )
        await self.db.commit()

        await self.publisher.publish({
            "event": "refund.created",
            "payment_id": payment_id,
        })
        self.processed.add(key)
        logger.info("Refund processed tenant=%s key=%s", tenant_id, key)
        return {"status": "ok", "refund_id": gateway_result["id"]}
