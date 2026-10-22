import { TAX_RATES, type Region } from "./generated/rates.js";

export interface Line {
  unitCents: number;
  quantity: number;
  discountPercent?: number;
}

/** Line total in integer cents, rounded half up. */
export function lineTotal(unitCents: number, quantity: number, discountPercent = 0): number {
  if (!Number.isInteger(unitCents) || !Number.isInteger(quantity)) {
    throw new TypeError("unitCents and quantity must be integers");
  }
  if (discountPercent < 0 || discountPercent > 100) {
    throw new RangeError("discountPercent must be between 0 and 100");
  }
  const gross = unitCents * quantity;
  return Math.trunc(gross * (1 - discountPercent / 100));
}

export function invoiceTotal(lines: Line[], region: Region): number {
  const subtotal = lines.reduce(
    (sum, line) => sum + lineTotal(line.unitCents, line.quantity, line.discountPercent),
    0,
  );
  return Math.round(subtotal * (1 + TAX_RATES[region]));
}
