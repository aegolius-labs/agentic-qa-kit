import { useState } from "react";
import { canBook } from "@booking/core";

export default function App({ existing }) {
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("10:00");
  const ok = canBook(existing, { start, end });
  return (
    <form>
      <input value={start} onChange={(e) => setStart(e.target.value)} />
      <input value={end} onChange={(e) => setEnd(e.target.value)} />
      <button disabled={!ok}>Book</button>
    </form>
  );
}
