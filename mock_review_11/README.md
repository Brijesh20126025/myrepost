# Blind Mock PR #11 — Investor Commitment API

## Context
A multi-tenant fund administration service exposes a FastAPI endpoint to create investor commitments and list commitments for a fund. You are reviewing a teammate's PR before release.

## Business requirements
1. A logged-in user may create and list commitments **only within their own tenant** and only with appropriate permissions.
2. The API accepts positive finite monetary amounts with no more than two decimal places. Preserve exact decimal precision.
3. The fund and investor must exist and belong to the caller's tenant. A commitment must not exceed the fund's remaining capacity.
4. Concurrent requests must never over-commit a fund. A client-supplied idempotency key is unique within the tenant; same key + same payload returns the original response; same key + different payload is rejected.
5. Commitment creation, aggregate updates, and outbox event insertion are atomic. Events are delivered by a separate retrying worker.
6. Listing supports a positive bounded page size, stable ordering and cursor pagination. Investor names should not trigger N+1 queries.
7. External risk checks are async, must have timeouts, and may be executed concurrently when independent. Failures must not be treated as approvals.
8. Return appropriate HTTP errors. Never expose internal exception details or sensitive information in logs.
9. The database is PostgreSQL and SQLAlchemy AsyncSession. Dependencies are intended to be request-scoped.
10. Tests must cover cross-tenant access, invalid money, duplicate requests, concurrent capacity checks, transaction failures and listing behavior.

## Review exercise
**Blind 45-minute mock.** Do not ask for an answer key until you have left GitHub inline comments.

Focus on correctness, security, data integrity, Python syntax/semantics, async, SQLAlchemy, performance, API behavior and tests.

For each finding, leave: **Severity / Original line / Why it fails / Production impact / Minimal fix / Test**.

The sample is intentionally not a standalone deployable app; model imports and dependency factories are assumed to exist in the surrounding service.
