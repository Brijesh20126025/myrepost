# Mock PR #7 — Fund Operations Platform (Advanced Blind Review)

## Interview simulation
You are the Senior Technical Lead reviewing a multi-file Python/FastAPI/PostgreSQL change submitted by another engineer. The change is **intentionally defective** and should **never be merged or deployed**. No answer key is provided. Aim for 75–100 minutes for this mega PR, or split into two 45-minute rounds.

## Business context
Juniper Square-like private-market administration. Tenants operate funds; investors subscribe to funds, administrators create capital calls, payments settle capital calls, and operators approve investor distributions. A background worker sends payment/distribution notifications. Users may have different roles and access to different funds.

## API contract
- POST /v1/capital-calls — create a fund capital call with a target amount and due date
- POST /v1/capital-calls/{call_id}/payments — record a payment with an idempotency key and gateway reference
- POST /v1/distributions/{distribution_id}/approve — approve a pending distribution, reserve/debit cash, and post ledger entries
- GET /v1/funds/{fund_id}/activity — list recent payments and distributions with pagination
- POST /v1/webhooks/payments — ingest a gateway payment status notification

## Requirements
1. Verify authentication; derive tenant and actor from a verified identity. Enforce role-based permissions and fund membership.
2. No cross-tenant or cross-fund data access; no PII or secrets in logs or external error messages.
3. Amounts must be positive and precise to cents. Payment and distribution totals must never exceed available limits.
4. Idempotency must be scoped and concurrency-safe. Same key with different request body must be rejected.
5. State transitions must be valid, atomic and race-safe; terminal states must not be reversed.
6. Balanced double-entry ledger writes and outbox events must commit with the corresponding financial state change.
7. External gateway calls cannot be rolled back by SQL transactions; handle timeouts, retries, duplicates and reconciliation.
8. Paginate deterministically, bound page sizes, avoid N+1 and unbounded scans.
9. Worker delivery is at-least-once, with atomic claiming, leases, retry limits and idempotent consumers.
10. Validate inputs at API and database boundaries; tests should exercise concurrent and failure paths.

## Technology
Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, PostgreSQL, pytest. The host application's actual authentication and database setup are intentionally represented by stubs; review those stubs as security-sensitive. This is not a deployable service.

## Review instructions
Open the GitHub **Files changed** tab. Leave inline comments with:
- severity (Critical/High/Medium/Low)
- exact failure scenario and production impact
- minimal concrete fix
- a test case where relevant

**Do not ask for an answer key until you finish.** When done, tell ChatGPT "Review my PR #7 comments". It will retrieve your comments, evaluate correctness and severity, identify missed findings, and show corrected snippets line by line.

## Suggested review order
schemas -> auth -> models -> repositories -> services -> API -> webhooks -> workers -> tests. You may discover cross-file issues that are not visible in one file.
