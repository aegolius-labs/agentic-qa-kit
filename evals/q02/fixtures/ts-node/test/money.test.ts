import { describe, expect, it } from "vitest";
import { invoiceTotal, lineTotal } from "../src/money.js";

describe("lineTotal", () => {
  it("multiplies unit price by quantity", () => {
    expect(lineTotal(250, 4)).toBe(1000);
  });

  it("applies a whole-cent discount", () => {
    expect(lineTotal(1000, 1, 10)).toBe(900);
  });

  it("rejects fractional cents", () => {
    expect(() => lineTotal(10.5, 1)).toThrow(TypeError);
  });
});

describe("invoiceTotal", () => {
  it("applies the region tax rate", () => {
    expect(invoiceTotal([{ unitCents: 1000, quantity: 1 }], "CA-ON")).toBe(1130);
  });
});
