from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Iterator, Sequence, TypeVar

T = TypeVar("T")
_WORD = re.compile(r"[A-Za-z']+")


def word_counts(text: str) -> dict[str, int]:
    """Count words case-insensitively. Apostrophes stay inside words."""

    return dict(Counter(word.lower() for word in _WORD.findall(text)))


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """Return the n most frequent words, ties broken alphabetically."""

    if n < 0:
        raise ValueError("n must not be negative")
    counts = word_counts(text)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:n]


def chunk(items: Sequence[T] | Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield consecutive lists of `size` items; the last one may be shorter."""

    if size <= 0:
        raise ValueError("size must be positive")
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
