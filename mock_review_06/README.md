# Mock PR #6 — Investor Distributions (blind review)

## Business context
A fund administrator creates investor distributions, approves them, and lists distribution history. This is a deliberately imperfect, multi-file Python/FastAPI/SQLAlchemy PR for a **45-minute Senior Technical Lead code review**. Do not merge or deploy.

## APIs
1. `POST /distributions`: Create a DRAFT distribution for a fund and investor.
2. `POST /distributions/{distribution_id}/approve`: Approve a distribution, debit fund cash, write ledger entries, enqueue an outbox event.
3. `GET /distributions`: List distributions with filters and pagination.

## Expected behavior
- Authenticated tenant and actor; investors must belong to the fund and tenant.
- Amounts are positive, exact USD cents; fund balance cannot go below zero.
- Approval is authorized, concurrency-safe, idempotent and atomic.
- Ledger remains balanced; event is durable and only emitted for committed approval.
- Pagination is stable and bounded; tenant isolation applies to all reads and writes.
- PII should not appear in logs or public errors.
- Tests should cover validation, state transitions, races, database failures, API behavior and query counts.

## Your task
Review the **Files changed** tab in GitHub. Comment on problematic lines with severity, failure scenario and minimal fix. There are issues spanning Python syntax/semantics, mutable defaults, Decimal, Pydantic, auth, transactions, PostgreSQL locking, SQLAlchemy ORM, idempotency, N+1, pagination, outbox and testing.

**No answer key is included in this PR** so you can review blind. After you post your review comments, ask me to evaluate them; I'll inspect the comments and score them, then produce a line-numbered corrected-code walkthrough.

## Environment
Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, PostgreSQL. Host application supplies the real DB session factory and authentication. Code is intentionally review-focused, not a deployable standalone service.
