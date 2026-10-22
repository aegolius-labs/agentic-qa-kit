# booking

Room booking monorepo.

| Path | What | Tests |
| --- | --- | --- |
| `packages/core` | Booking rules shared by the web app and the worker's API contract | `node --test` |
| `packages/web` | React front end | `vitest` |
| `services/worker` | Python job that expires unpaid holds | `python -m unittest` |

Run everything with `pnpm install && pnpm test`.

Bookings are half-open intervals `[start, end)`: a booking that ends at 10:00
does not overlap one that starts at 10:00.
