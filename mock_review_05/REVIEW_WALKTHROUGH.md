# Senior/Staff guided review — PR #5

This is an **answer key** for an intentionally defective PR. Read the implementation before the findings. Severity assumes a production multi-tenant financial platform. The snippets below are focused corrections, not a complete deployable patch.

## Review verdict: REQUEST CHANGES

The PR can cross tenant boundaries, overcollect under concurrency, double-charge an external gateway, create unbalanced ledgers, lose outbox events, and leak payment details. All are release blockers.

### Finding 1 — CRITICAL: Missing tenant authorization
**Files:** `repository.py` (`find_call`, `find_by_key`), `service.py` (`pay`), `api.py` (tenant/investor identity).

**Problem:** `find_call` selects by call ID only; tenant A can modify tenant B's capital call. Idempotency lookup by key alone can return a different tenant's payment. The API uses a hard-coded investor ID and a placeholder tenant function. The request doesn't prove that the investor owns the commitment/call.

**Failure:** A tenant A caller submits tenant B's capital call ID and causes a charge and balance change against B's call.

**Correction:**
```python
stmt = (
    select(CapitalCall)
    .where(CapitalCall.id == call_id, CapitalCall.tenant_id == tenant_id)
    .with_for_update()
)
call = db.scalar(stmt)
if call is None:
    raise NotFoundError("Capital call not found")
```
Authenticate tenant and investor through trusted identity, verify investor/commitment ownership, and scope idempotency to tenant. Use tenant-aware FK constraints where feasible.

### Finding 2 — CRITICAL: Overcollection under concurrent payments
**Files:** `service.py` (read remaining, then update), `repository.py` (`find_call`).

**Problem:** Two transactions both read remaining=100, each collect 80. Both gateway charges can succeed; application balance updates can lose an update or exceed the business cap. Python locks do not coordinate separate worker processes.

**Correction A:** Acquire PostgreSQL row lock with `SELECT ... FOR UPDATE` before checking remaining; keep lock until the single transaction commits.

**Correction B:** Atomic conditional update:
```sql
UPDATE capital_calls
SET collected_amount = collected_amount + :amount
WHERE id = :call_id
  AND tenant_id = :tenant_id
  AND collected_amount + :amount <= requested_amount
RETURNING id, collected_amount;
```
If zero rows returned, reject. This update must share a transaction with payment, ledger, and outbox writes. External gateway side effects require a separate state-machine/saga design.

### Finding 3 — CRITICAL: Idempotency race and missing DB uniqueness
**Files:** `models.py` (`Payment`), `repository.py` (`find_by_key`), `service.py`.

**Problem:** Read-before-insert is not atomic. Concurrent same-key requests can both pass the lookup and charge. No unique constraint exists. The lookup is not tenant-scoped and doesn't compare request payload.

**Correction:**
```python
from sqlalchemy import UniqueConstraint

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_payment_tenant_key"),
    )
    # columns...
```
Reserve a unique idempotency record *before* external effects; store canonical request fingerprint and processing state; replay only same payload. On unique violation, rollback then read existing record in a **fresh transaction**; if still processing, return/retry based on contract. A unique constraint alone is necessary but not sufficient for external charge safety.

### Finding 4 — CRITICAL: External gateway call before durable state
**Files:** `service.py` (gateway call preceding DB commit).

**Problem:** Gateway can charge successfully while the database commit fails. Retrying may charge again. Database rollback cannot reverse a remote payment.

**Recommended workflow:** (1) In a short DB transaction, validate/authorize and reserve an idempotent payment intent; (2) commit intent; (3) invoke gateway with a provider-supported idempotency key derived from the durable intent; (4) persist result and accounting entries in a separate atomic DB transaction, guarded by unique gateway reference and legal state transitions; (5) reconcile uncertain gateway timeouts by querying provider before retry. This is a state machine/saga, not a single ACID transaction across gateway and PostgreSQL.

### Finding 5 — CRITICAL: Ledger debit and credit are committed separately
**Files:** `service.py` (first `db.commit()` between ledger writes).

**Problem:** The first transaction persists the collected amount, payment and CASH debit. If the second transaction fails, the matching CAPITAL_RECEIVABLE credit is absent. Accounting is unbalanced.

**Minimal correction for DB-only writes:**
```python
with db.begin():
    # tenant-scoped call lock, amount checks, unique idempotency reservation
    # and conditional collected_amount update are inside this transaction.
    db.add(payment)
    db.flush()  # payment.id assigned, not committed
    db.add_all([
        LedgerEntry(payment_id=payment.id, account="CASH",
                    direction="DEBIT", amount=amount),
        LedgerEntry(payment_id=payment.id, account="CAPITAL_RECEIVABLE",
                    direction="CREDIT", amount=amount),
        OutboxEvent(payment_id=payment.id, event_type="PAYMENT_COMPLETED",
                    payload=payload),
    ])
# commit on success, rollback on error
```
This fragment assumes a new session with no active transaction and a **previously confirmed gateway outcome**. Do not place a remote gateway charge inside this DB transaction. SQLAlchemy 2.x autobegin means a query before `with db.begin()` can already open a transaction.

### Finding 6 — HIGH: Invalid money validation, float conversion, negative payments
**Files:** `schemas.py`, `service.py`.

**Problem:** `amount: float` and `Decimal(request.amount)` introduce binary float artifacts. No positivity/precision validation exists. A negative amount passes the `amount > remaining` check and subtracts from `collected_amount`, effectively reversing collections.

**Correction:**
```python
from decimal import Decimal
from pydantic import BaseModel, Field

class PayCapitalCallRequest(BaseModel):
    capital_call_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: str = Field(min_length=1, max_length=100)
```
Recheck invariants at service and DB layers; add `CHECK (collected_amount >= 0 AND collected_amount <= requested_amount)`, `CHECK (requested_amount > 0)`, and positive payment/ledger constraints. Consider enforcing USD currency explicitly.

### Finding 7 — HIGH: Outbox delivery is not safe with multiple workers
**Files:** `events.py`.

**Problem:** Two workers can select the same PENDING event and publish it twice. Broker publish can succeed, then the worker can crash before DB status commit, causing replay. Marking published before broker acknowledgement instead risks event loss. Exactly-once end-to-end delivery is not guaranteed by this pattern.

**Correction:** Claim batches using PostgreSQL `FOR UPDATE SKIP LOCKED` or atomic lease/claim updates; track attempt count and lease expiry. Publish with a stable event ID; mark delivered after broker ack; make consumers idempotent. Even with claims, crash windows imply **at-least-once** delivery.

**Illustrative claim query:**
```sql
SELECT id FROM outbox_events
WHERE status = 'PENDING'
ORDER BY id
FOR UPDATE SKIP LOCKED
LIMIT 100;
```
Claim in a short transaction and use a durable lease/state to avoid holding row locks across slow network I/O.

### Finding 8 — HIGH: Outbox is committed after financial writes
**Files:** `service.py`.

**Problem:** The outbox insert occurs after the first commit. If the second commit fails, a completed payment exists without a durable event to publish. The outbox record must be created in the same DB transaction as the final financial state change.

### Finding 9 — HIGH: Pagination is unstable and unbounded
**Files:** `repository.py` (`list_payments`), `api.py`.

**Problem:** `created_at DESC` is not a unique ordering. Equal timestamps can cause duplicate/missing records between pages. Offset pagination shifts when new rows arrive and grows expensive at high offsets. API permits negative/unbounded `limit` and `offset`.

**Correction:** Stable `ORDER BY created_at DESC, id DESC` and keyset pagination:
```sql
SELECT * FROM payments
WHERE tenant_id = :tenant_id
  AND (created_at, id) < (:cursor_time, :cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT :page_size;
```
Use the cursor condition only after the first page; index `(tenant_id, created_at DESC, id DESC)`; validate page size (e.g. 1..100). Do not assume a timestamp alone is unique.

### Finding 10 — MEDIUM/HIGH: N+1 queries when serializing
**Files:** `models.py` (`capital_call` lazy relationship), `api.py` (`p.capital_call.id`).

**Problem:** Accessing `p.capital_call` can trigger extra SELECTs for related capital calls (typically one per distinct related capital call not already in the identity map). For a 100-row page, this can add many queries.

**Correction:** For many-to-one, use `joinedload(Payment.capital_call)` or `selectinload`; here `Payment.capital_call_id` already exists, so simply use `p.capital_call_id` and avoid loading the relationship entirely.

### Finding 11 — HIGH: Webhook retry treats client errors as success
**Files:** `webhooks.py`.

**Problem:** `response.status_code < 500` treats 400/401/403/429 as delivered. It also blocks a worker with synchronous exponential sleeps, has no jitter, doesn't honor `Retry-After`, and does not persist delivery state or a stable delivery ID.

**Correction:** Define success as 2xx (possibly provider-specific). Retry timeouts, 429 and transient 5xx with bounded exponential backoff and jitter, usually via a durable queue; classify permanent 4xx as terminal; persist attempt counts and outcomes; sign payloads and include a stable delivery ID for receiver deduplication.

### Finding 12 — HIGH: Sensitive request logging
**Files:** `api.py`.

**Problem:** `logger.info("payment request %s", request.model_dump())` logs financial amount, identifiers and idempotency keys. Depending on policy, this may expose sensitive information in widely accessible logs.

**Correction:** Log a safe request/correlation ID, tenant ID where policy permits, result category, and latency; redact or hash sensitive fields. Never log gateway credentials, payment tokens, or raw request bodies.

### Finding 13 — HIGH: Missing ownership and request/response integrity
**Files:** `api.py`, `models.py`.

**Problem:** `investor_id=1001` is hard-coded; the request's capital call is not checked against investor/commitment ownership. No tenant-aware FK ties Payment to a CapitalCall of the same tenant. Response uses `float(result.amount)` (precision loss) and an ORM object may be expired after commit.

**Correction:** Derive investor identity from authenticated principal and check entitlement to the capital call. Add tenant-consistent constraints and return Decimal in the response schema. Prefer stable DTOs constructed after a controlled refresh or with known loaded values.

### Finding 14 — MEDIUM: Missing DB invariants and indexes
**Files:** `models.py`.

**Problem:** No unique constraint for tenant+idempotency key, no CHECK constraints on money, no status-state enforcement, no uniqueness on external gateway reference, and no index optimized for paginated tenant payments. Ledger entries lack a batch/journal identity and enforced balancing rules.

**Correction:** Use explicit `UniqueConstraint`, `CheckConstraint`, `Index`, foreign keys, and application-level posting rules. A simple per-row CHECK cannot by itself enforce that *multiple ledger rows sum to zero*; use an atomic posting service and appropriate reconciliation/DB enforcement strategy.

### Finding 15 — MEDIUM: Tests do not exercise actual behavior
**Files:** `tests/test_service.py`.

**Problem:** One mock-only missing-call test and one Decimal identity test cannot catch races, partial commits, tenant isolation, or outbox duplication.

**Recommended tests:**
1. Two concurrent payments of 80 against a call with 100 remaining: at most one succeeds.
2. Same key + same payload twice: one gateway charge, one payment.
3. Same key + different payload: conflict.
4. Tenant A cannot pay tenant B's call or fetch its idempotent result.
5. Ledger credit failure: no half-posted payment or collected balance change.
6. Outbox insert failure: financial state does not commit without event.
7. Gateway succeeds, DB fails: reconciliation prevents duplicate charge.
8. Two outbox workers: claim/lease logic, crash-after-publish replay.
9. Pagination with identical timestamps and concurrent inserts.
10. 400 vs 429 vs 503 webhook outcomes and backoff behavior.
11. Negative, zero, NaN, and over-precision amounts rejected.
12. Query-count test for payment listing.

Use real PostgreSQL for row locks, unique races and transaction isolation; SQLite tests are not equivalent.

## A corrected architecture, end-to-end

```text
POST /capital-calls/{id}/payments
   -> trusted auth / tenant / investor ownership
   -> validate Decimal amount + idempotency key
   -> DB transaction: reserve unique payment intent
   -> commit
   -> gateway charge with provider idempotency key
   -> DB transaction:
        verify legal payment state transition
        lock call or atomic conditional collection update
        insert balanced debit/credit ledger entries
        mark payment completed
        insert outbox event
      commit
   -> asynchronous outbox publisher (leased batches)
   -> broker (at-least-once)
   -> idempotent consumers / webhook delivery queue
```

**Important design nuance:** The external gateway may succeed after the call has become fully collected due to another in-flight payment. A robust design reserves remaining capacity *before* charging, or has a reliable reversal/refund and reconciliation path. A payment intent plus reservation accounting is preferable when there can be multiple simultaneous charges. Gateway requests need durable correlation IDs and a documented timeout/unknown-outcome state.

## Interview-ready summary

> I would request changes because the PR violates financial correctness under concurrency and lacks tenant authorization. The first blockers are cross-tenant access, unprotected remaining-balance checks, missing schema-backed idempotency, and split ledger/outbox commits. I'd redesign the workflow around durable payment intents, atomic capacity reservations, provider idempotency, balanced ledger posting and transactional outbox. Then I'd add PostgreSQL integration tests that reproduce two concurrent requests and gateway/DB partial failures. I would treat pagination and webhook retry policy as important follow-up issues, but not ahead of data integrity.

## Study checklist

- Explain `flush` vs `commit` vs `rollback` and SQLAlchemy autobegin.
- Explain `SELECT FOR UPDATE` vs conditional `UPDATE ... RETURNING`.
- Explain why Python locks do not protect multiple worker processes.
- Explain why a DB transaction cannot roll back an external gateway call.
- Explain why an outbox provides at-least-once, not guaranteed exactly-once.
- Explain why `joinedload` is often useful for many-to-one but unnecessary if FK ID suffices.
- Explain why an idempotency unique constraint is necessary but not sufficient.
