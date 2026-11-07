# Mock Review #8 — Python Syntax & Logic (Small PR)

**Goal:** Practice reading unfamiliar Python and finding language-specific bugs, not system design.

**Scenario:** A tiny in-memory fund allocation utility. The team wants to register investors, assign allocations, calculate totals, and format a summary.

**Review time:** 20–30 minutes. Review `allocations.py` and `tests/test_allocations.py` as if they were a colleague's PR.

**Expected behavior:**
- Every `AllocationBook` instance maintains independent investor and allocation state.
- Investor IDs are positive; names are nonblank. Registering the same ID twice is rejected.
- Allocations must be positive monetary values with at most two decimal places; no precision loss.
- Updating an investor's allocation replaces that investor's previous allocation.
- `total_allocated()` returns the exact sum; `remaining()` returns the exact unallocated amount.
- `find_investor(id)` returns the investor or `None` if absent.
- `top_investors(n)` returns at most n investors, highest allocation first, with deterministic tie-breaking by investor ID.
- `summary()` returns an independent snapshot; modifying the result must not mutate internal state.
- Tag normalization must not leak values across calls.
- Formatting an unknown investor must return a clear not-found result, not crash.

**Review focus:** Python syntax vs runtime behavior, class/instance variables, mutable defaults, aliasing, comprehensions, truthiness, iteration, sorting, Decimal, exceptions, tests.

There are intentional defects. **No answer key is included.** Add inline GitHub comments identifying exact issue, failure example, and minimal fix. When finished, ask ChatGPT: **Review my PR #8 comments**.
