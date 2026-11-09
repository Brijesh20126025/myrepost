# Blind PR #13: AsyncIO — Risk Check and Notifications

Review async/await, gather, return_exceptions, blocking I/O, cancellation, task supervision, shared sessions, and bounded concurrency.

## Review contract
This is a deliberately buggy teaching PR. Assume the relevant model/dependency interfaces exist in the surrounding application. Review each changed line for correctness, concurrency, security, performance, API semantics, failure behavior, and missing tests. Leave inline severity, concrete failure scenario, minimal fix and test. **No answer key is provided until after your review.**
