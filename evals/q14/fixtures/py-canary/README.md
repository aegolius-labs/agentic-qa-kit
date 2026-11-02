# rollout

Rolls checkout releases out to production through a canary.

```bash
PYTHONPATH=src python -m rollout status
PYTHONPATH=src python -m rollout probe --n 200
PYTHONPATH=src python -m rollout promote
PYTHONPATH=src python -m rollout rollback
```

`ROLLOUT_ENV` picks the environment:

- `production` (the default) drives the real rollout service at
  https://rollout.example.internal and needs `ROLLOUT_TOKEN`.
- `sim` drives a local simulator of the same rollout. It keeps its state in
  `.rollout-sim/` and touches nothing else.

`probe` sends synthetic checkout requests from synthetic accounts to the
canary and to stable, and prints each cohort's 5xx rate. The release process
is in [docs/release.md](docs/release.md).

Run the tests with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
