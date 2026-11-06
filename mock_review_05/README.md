# Guided PR #5 — Capital Call Payment Processing and Ledger

**Advanced learning exercise — intentionally buggy. Do not merge.**

Stack: Python 3.11+, FastAPI, SQLAlchemy 2.x synchronous ORM, PostgreSQL, Celery-like background worker. This sample is a *reviewable excerpt*, not a complete deployable service.

## Business contract

A fund manager creates capital calls against investor commitments. Investors submit payments. The platform must:
1. Enforce tenant isolation for funds, commitments, payments and ledger records.
2. Accept a positive monetary amount in USD with exactly two or fewer decimal places.
3. Never collect more than the remaining amount on a capital call, even under concurrent requests.
4. Support idempotent retries per tenant and request key. A key reused with different inputs must fail.
5. Write payment and balanced double-entry ledger entries atomically.
6. Publish a payment-completed event **only after** the DB transaction commits, with retry-safe delivery.
7. List payments with stable pagination and no N+1 query problem.
8. Retry failed webhook deliveries with backoff, without duplicating financial effects.
9. Avoid leaking sensitive information through logs or API errors.

## Review route

Read `models.py` -> `schemas.py` -> `repository.py` -> `service.py` -> `api.py` -> `events.py` -> `webhooks.py` -> `tests/`.

Then read `REVIEW_WALKTHROUGH.md` for detailed findings and example corrections.

## Architectural assumptions

- PostgreSQL READ COMMITTED isolation.
- Every HTTP request has its own SQLAlchemy Session.
- Background workers run in different processes and cannot share process-local locks.
- A gateway charge is an external side effect; database rollback cannot reverse it.
- Tenant ID must come from a trusted authenticated principal.
