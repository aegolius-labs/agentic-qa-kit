/** Minutes since midnight for "HH:MM". */
export function toMinutes(hhmm) {
  const match = /^(\d{2}):(\d{2})$/.exec(hhmm);
  if (!match) throw new Error(`bad time: ${hhmm}`);
  const [h, m] = [Number(match[1]), Number(match[2])];
  if (h > 23 || m > 59) throw new Error(`bad time: ${hhmm}`);
  return h * 60 + m;
}

/** Bookings are half-open [start, end). */
export function overlaps(a, b) {
  return toMinutes(a.start) <= toMinutes(b.end) && toMinutes(b.start) <= toMinutes(a.end);
}

export function canBook(existing, candidate) {
  if (toMinutes(candidate.start) >= toMinutes(candidate.end)) return false;
  return !existing.some((booking) => overlaps(booking, candidate));
}
