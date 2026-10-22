# retry

`retry` runs a command until it succeeds, waiting with capped exponential
backoff between attempts.

```bash
go run ./cmd/retry -attempts 5 -base 200ms -max 2s -- ./flaky.sh
```

The delay before retry `n` (counting from 1) is `base * 2^(n-1)`, never more
than `max`. With `-attempts 5` the command runs at most five times.

## Development

`make test` runs the unit tests and `make lint` runs golangci-lint.
