# BLIND FINAL 2 — AsyncIO, Concurrency, Retry & Cache

**BLIND REVIEW — NO ANSWER KEY OR INLINE SOLUTIONS.**

## PR intent
Risk checks should not block; failure must fail closed. Notifications durable; bounded concurrency; cancellation works. Cache must isolate tenants and refresh.

## Review contract
You are a Senior Technical Lead reviewing a teammate's unfamiliar Python PR. Assume surrounding ORM models, dependencies and external services exist unless the changed code itself makes an invalid assumption. Find confirmed bugs and distinguish conditional concerns. Add inline GitHub review comments: **severity, original line, impact/failure example, minimal fix, and a test**. Prioritize business logic, Python idioms, API semantics, DB transactions, concurrency, security, performance, and missing tests.

Aim for 30–45 minutes. Do not run the code as a substitute for tracing behavior. No answer key will be published until after your review.
