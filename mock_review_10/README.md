# Guided Review #10 — Payment Refund API

**Mode:** Study the expert inline comments first. Unlike PR #8/#9, this is an **annotated teaching PR**, not a blind test.

## Business contract
- `POST /refunds` requests a refund for a captured payment belonging to the authenticated tenant.
- Request amount must be positive, finite, at most 2 decimal places, and no greater than remaining refundable balance.
- Repeated requests with the same tenant-scoped idempotency key must return the same result, without calling the gateway again.
- Concurrent refunds cannot exceed the original captured amount.
- Gateway requests use stable provider idempotency keys and do not expose secrets in logs.
- DB updates, refund records and outbox events must be transactionally consistent.
- Async request handling must not block the event loop.
- Outbox workers may retry and must avoid concurrent duplicate claims and duplicate externally visible effects.
- API must enforce tenant authorization and return appropriate 4xx errors.
- Tests cover duplicate requests, concurrency, invalid money, authorization, gateway errors and retries.

## How to study
1. Open **Files changed**, read a small block, then open its inline reviewer comment.
2. For each comment: identify the failing input/race, explain the production impact, and read the minimal fix.
3. Try writing your own fix before opening the next comment.
4. No real gateway or database is connected; this code is deliberately incomplete/unsafe and is not intended to deploy.

After this guided review, ask for a **blind timed PR #11** to test your retention.
