# Commitment Reporting

A lightweight Python-only feature for summarizing fund commitments. No database or HTTP server is needed.

## Requirements

- Commitments have an integer ID, a fund ID, an investor ID, an amount in decimal currency units, and a status.
- Only ACTIVE commitments count toward a fund's committed total.
- Listing a fund's commitments must return records sorted by amount (largest first) without changing the stored order.
- An optional minimum amount is inclusive; an omitted minimum means no minimum.
- The investor breakdown returns one total per investor, including investors with multiple commitments.
- An export produces a separate dictionary for each commitment and must not change stored data.
- Unknown funds return an empty list and a zero total.
- Invalid commitment amounts must be rejected, not silently ignored.

## Run tests

```bash
python -m pytest mock_review_02/tests -q
```

Review the changes as a normal pull request; no answer key is provided.
