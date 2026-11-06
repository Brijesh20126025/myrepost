import json

from sqlalchemy import select
from .models import OutboxEvent


def publish_pending_events(db, broker, batch_size=100):
    events = db.scalars(
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING")
        .limit(batch_size)
    ).all()

    for event in events:
        broker.publish(event.event_type, json.loads(event.payload))
        event.status = "PUBLISHED"

    db.commit()
    return len(events)
