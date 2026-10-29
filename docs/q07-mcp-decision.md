# Q07: keep the skills-only architecture

Decided 2026-10-29 on the evidence below. Revisit when a trigger at the end
holds.

## Question

Q07 asks whether host tools plus the local ledger leave authorization,
compact-query, portability or structured-result gaps that an MCP server would
close. The answer decides between keeping skills plus `scripts/qa.py` and
building a narrowly scoped server.

## Evidence

`scripts/q07_measure.py` read the 18 retained `claude -p` transcripts from the
Q02, Q04 and Q05 lanes (2026-10-22 to 2026-10-29). The per-session numbers are
in
[`evals/results/q07-transcript-measure-2026-10-29.json`](../evals/results/q07-transcript-measure-2026-10-29.json).
The Q01 activation lane is excluded because its cases mostly stop before
writing to the ledger.

| Measure | Value |
| --- | --- |
| Sessions | 18 (USD 10.82) |
| Tool calls | 313 |
| Calls spent learning payload shapes (plugin `src/`, `examples/`, docs, `--help`) | 72 (23%), in all 18 sessions |
| Bytes those calls returned | 188 KB of 544 KB tool output (35%), about 10 KB per session |
| Ledger writes through `qa.py` | 100 |
| Writes the ledger rejected | 23 |
| Host permission denials | 1 (Q02 `py-service`) |

The 23 rejections, by cause:

- 7 restated `finding.reproduction.attempts`, a count the ledger already
  knows from `attempt_ids`, and got it wrong.
- 9 used a value outside an enum: quality attribute, session mode, charter
  status, attempt outcome, obligation technique, or reproducibility. Each error
  named the allowed values.
- 4 passed the session to `summary` positionally, as `show` and
  `session-close` take it.
- 3 sent the wrong shape: a field the finding schema does not have, or a
  `reproduction` that was not an object.

## Reading of each gap

- **Authorization.** No session wrote the ledger except through the CLI, and
  every rejected write left the session unchanged. Both boundary cases in Q05,
  and every Q02 case, stopped at the authority boundary through the skills. In
  the one case where the host denied a call, the host's permission layer
  enforced the boundary. A server would add a second permission surface that
  the host must still be trusted to enforce. It would not add authority. No gap.
- **Compact query.** Real and measured: about a quarter of tool calls and a
  third of tool output go on learning payload shapes. An MCP server's typed
  tool schemas would carry the enums, but they would load into every session
  whether or not it writes to the ledger, at a size comparable to the 10 KB
  spent now. Most of the rejected writes were CLI ergonomics, not missing
  structure, and the CLI can fix them directly (below). Not a reason to build
  a server.
- **Portability.** The kit runs wherever Python 3.11+ and a shell do: Linux,
  macOS and Windows in CI, on Claude Code and Codex. A server would need the
  host to register and launch it, and it would bring a dependency the runtime
  rule excludes, unless it speaks JSON-RPC by hand. No gap that a server
  closes.
- **Structured results.** Every command already prints JSON, and `summary`
  is bounded by `scripts/budgets.py`. No gap.

## Decision

Keep the skills-only architecture. Fix the measured CLI friction in the same
change:

- The ledger counts `reproduction.attempts` from `attempt_ids` when the
  caller leaves it out, on `finding-add` and on `finding-update`. A supplied
  count is still checked, and the error now states the expected number.
- `summary` takes the session positionally, as `show` and `session-close`
  do, and still accepts `--session`.

## Revisit when

- a supported host cannot run local Python or a shell;
- authorization has to be enforced by a broker outside the host's permission
  layer, for example for Q08's agentic-system assurance;
- after these fixes, a repeat measurement still shows payload discovery
  above about 20% of tool calls (Q07-G01).
