# batchtools

Small helpers for preparing job batches.

- `dedupe(items)` removes duplicates and keeps the order in which items first
  appear: `dedupe(["b", "a", "b"])` is `["b", "a"]`.
- `batches(items, size=None)` splits items into lists of at most `size`. With
  no size it uses `DEFAULTS["batch_size"]`, which is 10.
- `configure(**overrides)` changes the defaults for later calls.

Run the tests with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

The suite is a little flaky in CI, so CI retries it up to three times.
