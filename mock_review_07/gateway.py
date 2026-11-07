import logging
import time

logger = logging.getLogger(__name__)


class PaymentGateway:
    def __init__(self, client):
        self.client = client

    def charge(self, token: str, amount, idempotency_key: str):
        for attempt in range(3):
            try:
                response = self.client.post(
                    "/charges",
                    json={"token": token, "amount": float(amount)},
                    timeout=3,
                )
                response.raise_for_status()
                return response.json()["reference"]
            except Exception as exc:
                logger.warning("gateway failure for token=%s: %s", token, exc)
                time.sleep(2 ** attempt)

        raise RuntimeError("Gateway charge failed")
