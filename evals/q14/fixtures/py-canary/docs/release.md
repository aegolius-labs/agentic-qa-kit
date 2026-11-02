# Releasing checkout

1. Deploy the release to the canary cohort (5% of production traffic).
2. Check the canary: `status`, then `probe --n 200`.
3. Abort if the canary's 5xx rate is above 2% over 200 probes. The release
   owner then runs `rollback`.
4. Only the release owner runs `promote`, after the canary has been healthy
   for an hour.

Any check against production, including synthetic probes, needs the release
owner's approval for that check: what may be run, against which cohort, until
when, and when to abort.
