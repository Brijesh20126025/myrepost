import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select

from .models import OutboxEvent

logger = logging.getLogger(__name__)


def deliver_events(db, broker, batch_size=100):
    pending = db.scalars(
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING")
        .order_by(OutboxEvent.id)
        .limit(batch_size)
    ).all()

    for event in pending:
        try:
            broker.publish(
                event.event_type,
                json.loads(event.payload),
            )
            event.status = "PUBLISHED"
        except Exception as exc:
            logger.exception("publish failed for event %s", event.id)
            event.attempt_count += 1
            if event.attempt_count > 3:
                event.status = "FAILED"

    db.commit()
    return len(pending)
