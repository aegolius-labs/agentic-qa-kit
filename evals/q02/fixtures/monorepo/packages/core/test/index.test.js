import { test } from "node:test";
import assert from "node:assert/strict";
import { canBook, overlaps, toMinutes } from "../src/index.js";

test("parses times", () => {
  assert.equal(toMinutes("09:30"), 570);
  assert.throws(() => toMinutes("24:00"));
});

test("detects a clear overlap", () => {
  assert.equal(overlaps({ start: "09:00", end: "10:00" }, { start: "09:30", end: "10:30" }), true);
});

test("rejects an empty booking", () => {
  assert.equal(canBook([], { start: "10:00", end: "10:00" }), false);
});
