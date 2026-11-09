# Blind PR #14: SQLAlchemy — Commitments and Capacity

Review session lifecycle, transaction atomicity, autoflush, row locking, N+1, joinedload collection, pagination and DB constraints.

## Review contract
This is a deliberately buggy teaching PR. Assume the relevant model/dependency interfaces exist in the surrounding application. Review each changed line for correctness, concurrency, security, performance, API semantics, failure behavior, and missing tests. Leave inline severity, concrete failure scenario, minimal fix and test. **No answer key is provided until after your review.**
