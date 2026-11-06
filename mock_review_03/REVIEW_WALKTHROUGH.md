# Guided code review: Python collections and object behavior

**How to use this:** First read the implementation files, then read each numbered finding. For each finding, predict the output before reading the explanation. These are teaching notes, not production code changes.

## 1. HIGH — Class attribute shared between repository instances
**File:** `repository.py:5`

```python
class PaymentRepository:
    payments = {}
```

`payments` is attached to the class, so independent `PaymentRepository()` objects share one dictionary. A test may see records inserted by another test.

**Fix:**
```python
class PaymentRepository:
    def __init__(self):
        self.payments = {}
```

**Python concept:** class attributes vs instance attributes; `self`.

## 2. MEDIUM — Mutable default argument and aliasing
**File:** `service.py:9`

```python
def create(self, payment, labels=[]):
    payment.labels = labels
```

Python evaluates `[]` once at function definition time. Multiple calls without labels can share the same list. Even when a caller passes a list, assigning it directly aliases that caller's list.

**Fix:**
```python
def create(self, payment, labels=None):
    payment.labels = list(labels) if labels is not None else []
```

**Python concept:** mutable objects, default arguments, shallow copies.

## 3. HIGH — Dictionary comprehension overwrites duplicate keys
**File:** `service.py:18-22`

```python
return {p.investor_id: p.amount for p in self.paid_payments()}
```

If investor 10 has paid payments of 50 and 100, the dictionary ends with `{10: Decimal("100")}`, not 150. A dict can have only one value per key.

**Fix:**
```python
totals = {}
for p in self.paid_payments():
    totals[p.investor_id] = totals.get(p.investor_id, Decimal("0")) + p.amount
return totals
```

**Python concept:** dictionary comprehensions, `dict.get`, aggregation.

## 4. HIGH — Monetary amounts sorted as strings
**File:** `service.py:24-29`

`str(p.amount)` sorts lexicographically. For 9, 50, 100, descending string order is 9, 50, 100, not 100, 50, 9.

**Fix:** `key=lambda p: p.amount`.

**Python concept:** `sorted`, `lambda`, numeric vs string comparison.

## 5. HIGH — Reusing one dictionary in a loop
**File:** `service.py:32-38`

The `row = {}` dictionary is created once, outside the loop. `result.append(row)` appends the *same object reference* repeatedly. All rows ultimately show the last payment's ID. The `labels` list is also returned by reference.

**Fix:**
```python
return [
    {"id": p.id, "labels": list(p.labels)}
    for p in self.repository.all()
]
```

**Python concept:** list references, identity, copying, comprehensions.

## 6. HIGH — Generator truthiness does not mean it has items
**File:** `service.py:41-45`

`matches = (p for p in ...)` creates a generator. The generator object is truthy even if it will yield no matches. `next(matches)` raises `StopIteration` on exhaustion.

**Fix:**
```python
return next(
    (p for p in self.paid_payments() if p.amount > threshold),
    None,
)
```

**Python concept:** lazy generators, `next(iterator, default)`, `StopIteration`.

## 7. MEDIUM — Missing duplicate-ID and input validation
**Files:** `repository.py:8`, `models.py:6-11`

The repository overwrites an existing payment with the same ID. The dataclass type hints do not validate types or positive amounts at runtime.

**Fix:** Validate IDs and amounts in `Payment.__post_init__`; reject duplicate IDs in a distinct `add` operation. Do not confuse Python type hints with runtime validation.

## 8. MEDIUM — Tests are weak and can interfere with each other
**File:** `tests/test_payments.py`

The tests only check a count and use `>= 2` rather than exact expected records. Class-level shared storage means earlier tests affect later tests.

**Better tests:** two repository instances are isolated; two payments for one investor aggregate; sorted 9/50/100; export rows have distinct IDs; modifying exported labels does not mutate stored labels; no generator match returns `None`; duplicate IDs are rejected.

## Review-summary example

**Request changes.** This PR has multiple correctness issues: shared repository state, incorrect investor totals, incorrect numeric ordering, aliased export rows, and an unhandled generator exhaustion case. I'd prioritize fixing those and adding regression tests before approval. Style-only suggestions should come after these blockers.
