# Mock PR #9 — Async/Await, Generators, Iterators & Comprehensions

**Timebox:** 25–35 minutes. Small Python/FastAPI review. Review blind; no answer key.

## Scenario
A fund administration API returns a compact dashboard for a fund: recent payment rows, total settled amount, unique investor IDs, and enriched investor names from a remote directory.

## Requirements
1. GET `/funds/{fund_id}/dashboard` returns the correct data for that fund only.
2. Payment amounts are represented exactly as `Decimal`; totals count only SETTLED payments.
3. The repository provides an iterator over payment rows; the dashboard must not lose data by exhausting it prematurely.
4. The investor directory is async and should be queried concurrently when safe; all work must finish before returning.
5. No blocking sleeps in async request handlers; no unmanaged fire-and-forget tasks.
6. Missing investor names are represented as `"Unknown"`; duplicate investor IDs must not cause redundant directory requests.
7. Recent payment IDs are in descending timestamp order, tie-broken by ID, limited to a positive bounded limit.
8. A streaming generator should produce each settled payment exactly once and clean up database resources.
9. A failure in a remote directory lookup should not silently produce a successful but incorrect financial total.
10. The code should be testable, and tests should cover async behavior, iterator exhaustion, sorting, filtering and edge cases.

## Instructions
Read `dashboard.py` and `tests/test_dashboard.py`. Leave inline GitHub review comments with: severity, failing example, and minimal fix. Focus on Python semantics, not full-scale distributed system architecture. The service dependencies are intentionally small protocols/stubs; no live DB or external API is required to review.

When done, ask ChatGPT: **Review my PR #9 comments**.
