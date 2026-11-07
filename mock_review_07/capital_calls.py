import logging
from datetime import datetime

from .models import CapitalCall, OutboxEvent
from .repositories import CapitalCallRepository, FundRepository

logger = logging.getLogger(__name__)


class CapitalCallService:
    def __init__(self):
        self.calls = CapitalCallRepository()
        self.funds = FundRepository()

    def create(self, db, tenant_id: int, actor_id: int, request):
        fund = self.funds.get(db, request.fund_id)
        if fund is None:
            raise ValueError("Fund not found")

        if request.due_at < datetime.utcnow():
            raise ValueError("Due date is in the past")

        call = CapitalCall(
            tenant_id=tenant_id,
            fund_id=request.fund_id,
            target_amount=request.target_amount,
            collected_amount=0,
            status="OPEN",
            due_at=request.due_at,
        )
        db.add(call)
        db.flush()

        db.add(OutboxEvent(
            tenant_id=tenant_id,
            event_type="CAPITAL_CALL_CREATED",
            aggregate_id=call.id,
            payload='{"call_id": %d}' % call.id,
        ))
        db.commit()
        logger.info("created call %s for tenant %s", call.id, tenant_id)
        return call
