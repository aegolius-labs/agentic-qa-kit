"""Small helpers for preparing job batches."""

DEFAULTS = {"batch_size": 10}


def dedupe(items):
    """Return items without duplicates, keeping the order of first occurrence."""
    return list(set(items))


def configure(**overrides):
    """Update the defaults used by later calls and return the new defaults."""
    DEFAULTS.update(overrides)
    return dict(DEFAULTS)


def batches(items, size=None):
    """Split items into lists of at most `size` items, by default DEFAULTS["batch_size"]."""
    size = size or DEFAULTS["batch_size"]
    return [items[start:start + size] for start in range(0, len(items), size)]
