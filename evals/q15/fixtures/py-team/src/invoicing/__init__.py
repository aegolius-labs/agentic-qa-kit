"""Invoice totals."""

from decimal import ROUND_HALF_UP, Decimal


def total(lines: list[tuple[str, int]]) -> Decimal:
    """Sum (unit price, quantity) lines, rounded half up to the cent."""
    amount = sum(Decimal(price) * quantity for price, quantity in lines)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
