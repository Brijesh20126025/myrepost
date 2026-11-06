# Guided PR #4 — Withdrawals (FastAPI + SQLAlchemy 2.x)

**Learning exercise only. Do not deploy or merge.** This intentionally flawed PR simulates a financial withdrawal endpoint.

## Expected contract
- Investors belong to a tenant; an authenticated caller may withdraw only from their tenant.
- Amount must be positive, in decimal currency units; insufficient funds must fail.
- Balance deduction, withdrawal creation, and audit event must commit atomically.
- A retry with the same tenant + idempotency key + identical request returns the original withdrawal, without a second deduction.
- Reusing the same key for a different request is a conflict.
- Two simultaneous withdrawals must never overspend a balance.
- Failed operations must not create withdrawals or audit events.

## Files
- `models.py`: ORM tables
- `schemas.py`: API request validation
- `repository.py`: database access
- `service.py`: business workflow
- `api.py`: FastAPI route
- `tests/test_withdrawals.py`: starter tests
- `REVIEW_WALKTHROUGH.md`: detailed senior-level answer key

Assume PostgreSQL, SQLAlchemy 2.x synchronous sessions, and a properly configured `SessionLocal` factory. The example is intentionally not a fully wired runnable application. The code review focuses on correctness and transaction boundaries.
