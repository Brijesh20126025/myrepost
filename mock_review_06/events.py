import json

from sqlalchemy import select

from .models import OutboxEvent


def publish_pending(db, broker, batch_size=50):
    rows = db.scalars(
        select(OutboxEvent)
        .where(OutboxEvent.status == "PENDING")
        .limit(batch_size)
    ).all()

    for row in rows:
        broker.publish(row.event_type, json.loads(row.payload))
        row.status = "PUBLISHED"

    db.commit()
    return len(rows)
