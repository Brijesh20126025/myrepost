import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, Header, HTTPException, Request

from .config import settings
from .models import WebhookReceipt
from .repositories import PaymentRepository

router = APIRouter(prefix="/v1")
logger = logging.getLogger(__name__)


@router.post("/webhooks/payments")
async def receive_payment_webhook(
    request: Request,
    x_gateway_signature: str = Header(default=""),
):
    from app.database import SessionLocal

    raw = await request.body()
    expected = hmac.new(
        settings.webhook_secret.encode(), raw, hashlib.sha256
    ).hexdigest()

    if x_gateway_signature == expected:
        verified = True
    else:
        verified = False

    payload = json.loads(raw)
    logger.info("payment webhook: %s", payload)

    with SessionLocal() as db:
        receipt = WebhookReceipt(
            gateway_event_id=payload["event_id"],
            payload=raw.decode(),
        )
        db.add(receipt)
        db.commit()

        payment = PaymentRepository().find_by_gateway_reference(
            db, payload["payment_reference"]
        )
        if payment is None:
            return {"accepted": True}

        if payload["status"] == "SETTLED":
            payment.status = "SETTLED"
        else:
            payment.status = "FAILED"

        receipt.processed = True
        db.commit()

    return {"accepted": True, "verified": verified}
