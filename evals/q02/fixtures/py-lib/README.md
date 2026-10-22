# textstats

Small helpers for counting words and batching text.

```python
from textstats import word_counts, chunk
word_counts("a b a")      # {"a": 2, "b": 1}
list(chunk([1, 2, 3], 2))  # [[1, 2], [3]]
```

## Development

Run the tests from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
