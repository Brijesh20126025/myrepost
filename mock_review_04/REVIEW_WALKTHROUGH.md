# Guided senior-level code review — database transactions and concurrency

Read the code first, then use these findings as an answer key. **Severity** assumes a real multi-tenant financial product. This is an educational example, not an exhaustive production implementation.

## 1. CRITICAL — Tenant isolation is missing
**Location:** `repository.py:8-13`, `service.py:17-19`

The investor query uses only `Investor.id`, so a caller from tenant A can request a withdrawal against an investor from tenant B. The withdrawal is then recorded with tenant A's ID even though it changed B's balance.

**Fix:** Authenticate tenant identity, authorize the investor, and scope every relevant query to tenant. For example:

```python
select(Investor).where(
    Investor.id == investor_id,
    Investor.tenant_id == tenant_id,
).with_for_update()
```

The placeholder `current_tenant_id()` in `api.py` must be replaced by trusted authentication/authorization; never accept tenant identity directly from untrusted request input.

## 2. CRITICAL — Race condition: two withdrawals can overspend
**Location:** `service.py:22-26`

Two transactions can read the same balance (say 100), both see enough for an 80 withdrawal, and both proceed. Without a row lock or an atomic conditional update, the balance and withdrawal records may disagree, and the business limit can be violated.

**Option A:** In PostgreSQL, lock the investor row with `SELECT ... FOR UPDATE` *inside the transaction* and then check/deduct the balance. Concurrent requests for the same investor serialize.

**Option B:** Atomic conditional SQL update:

```sql
UPDATE investors
SET balance = balance - :amount
WHERE id = :investor_id
  AND tenant_id = :tenant_id
  AND balance >= :amount
RETURNING balance;
```

Require exactly one returned row or reject. The update and withdrawal insert must be in the **same transaction**.

## 3. CRITICAL — Idempotency is not concurrency-safe
**Location:** `repository.py:11-14`, `models.py:19-27`

The application checks for an existing key before inserting, but two requests can both see no row and both create withdrawals. The schema has **no unique constraint** on `(tenant_id, idempotency_key)`. The lookup also ignores tenant ID.

**Fix:** Add `UniqueConstraint("tenant_id", "idempotency_key")` to `Withdrawal`. Look up by both tenant and key, handle the unique-conflict race in a fresh transaction, and return the stored result only after verifying that the request payload (investor ID, amount, etc.) matches the original. A conflicting reuse of a key must fail. A robust workflow can reserve an idempotency record first and serialize same-key requests; unique constraint alone prevents duplicates but does not define retry behavior.

## 4. CRITICAL — Commit splits one logical operation into two transactions
**Location:** `service.py:34-46`

The withdrawal and balance change are committed before the audit event. If audit insertion fails, `rollback()` cannot undo the *already committed* withdrawal. The exception is swallowed, so the endpoint can report success with no audit record.

**Fix:** Add the withdrawal and audit event within one transaction; `flush()` assigns the withdrawal ID before the audit insert. Commit only once:

```python
# Illustrative fragment; db is a fresh Session with no active transaction.
with db.begin():
    # tenant-scoped locked investor read, validation and idempotency
    # checks must also happen inside this block.
    db.add(withdrawal)
    db.flush()  # assigns withdrawal.id; does not commit
    db.add(AuditEvent(
        withdrawal_id=withdrawal.id,
        action="WITHDRAWAL_COMPLETED",
    ))
# successful exit commits; exceptions roll back
```

**SQLAlchemy 2.x subtlety:** Executing a query often starts a transaction automatically (autobegin). Do not query first and then call `with db.begin()` on the same active session without addressing that state. Put the whole operation inside the transaction from the start. After a commit, expired ORM attributes may trigger additional queries on access depending on session configuration.

## 5. HIGH — Money is modeled as `float`, then converted incorrectly
**Location:** `schemas.py:6-8`, `service.py:21`

Binary floats are not appropriate for decimal currency. `Decimal(request.amount)` captures the binary floating-point approximation. Use Pydantic `Decimal` validation and enforce positivity and currency precision.

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class WithdrawalRequest(BaseModel):
    investor_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: str = Field(min_length=1, max_length=100)
```

In the service, use the validated `Decimal` directly. Also check tenant-specific business limits where applicable.

## 6. CRITICAL — Negative amount increases balance
**Location:** `service.py:22-26`

There is no `amount > 0` validation. With a negative amount, `investor.balance < amount` is typically false, and `investor.balance -= amount` **adds** money. Zero withdrawals are also accepted.

**Fix:** Enforce positive amounts at the API boundary and again in the domain/service boundary if callers can bypass the API.

## 7. HIGH — Missing request fingerprint for idempotency
**Location:** `service.py:13-15`

Reusing an idempotency key with a different investor or amount returns an unrelated old withdrawal. Even after adding a unique key, check that the original request fields match the retry. A canonical request fingerprint can be stored alongside the key.

**Fix:** On replay, compare tenant, investor, amount, and any other meaningful request fields. Return 409 Conflict for mismatched reuse.

## 8. HIGH — ORM transaction and error handling are underspecified
**Location:** `service.py:12-48`, `api.py:33-34`

An `IntegrityError`, database timeout, or commit failure is not mapped to a controlled response. After a failed flush/commit, a SQLAlchemy session generally needs a rollback before reuse. Also, after `commit()`, accessing expired ORM attributes can trigger new database reads.

**Fix:** Keep one transaction owner (service/unit of work); let transaction context roll back on failure; catch expected domain errors separately from unexpected DB failures, and map them at the API boundary. Avoid hiding database failures behind generic success.

## 9. MEDIUM — Tests miss all financial invariants
**Location:** `tests/test_withdrawals.py`

The mocked test only checks missing-investor behavior. The second test is a placeholder. Neither exercises actual PostgreSQL transactions.

**Add integration tests:** same-tenant withdrawal success; cross-tenant access denied; insufficient and negative amounts; same-key retry; same-key different payload conflict; two concurrent withdrawals against a 100 balance; audit insertion failure rolls back balance and withdrawal; duplicate-key race. Use PostgreSQL for `FOR UPDATE` semantics, not SQLite.

## 10. MEDIUM — Indexing and schema constraints
**Location:** `models.py`

Add database constraints appropriate for a financial domain: nonnegative balance check, positive withdrawal amount, foreign keys with tenant-consistent ownership, a unique idempotency key scoped by tenant, and useful query indexes. A plain foreign key on investor ID alone does not enforce that withdrawal tenant matches investor tenant. A composite foreign key or equivalent enforcement can protect this invariant.

## Suggested review summary

**Request changes — blocking financial correctness and isolation issues.** The current workflow permits cross-tenant balance changes, concurrent overspending, duplicate withdrawals on retries, negative withdrawals, and partial commits without audit events. I'd require tenant-scoped locking/atomic balance deduction, schema-backed idempotency, one transaction for all writes, Decimal validation, and PostgreSQL integration tests before approving.

## Study order

1. `with db.begin()`, `flush()`, `commit()`, `rollback()`
2. Lost updates and `SELECT ... FOR UPDATE`
3. Atomic conditional `UPDATE ... RETURNING`
4. Idempotency: precheck vs unique constraint vs replay
5. Tenant isolation and database constraints
6. SQLAlchemy autobegin, exception handling, integration tests
