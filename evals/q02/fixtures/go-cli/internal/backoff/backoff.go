// Package backoff computes capped exponential retry delays.
package backoff

import "time"

// Delay returns the wait before retry n (n >= 1): base * 2^(n-1), capped at max.
func Delay(n int, base, max time.Duration) time.Duration {
	if n < 1 {
		return 0
	}
	d := base
	for i := 1; i < n; i++ {
		d *= 2
	}
	if d > max {
		return max
	}
	return d
}

// Schedule returns the delays between the attempts of a run that makes at
// most `attempts` tries: one delay fewer than attempts.
func Schedule(attempts int, base, max time.Duration) []time.Duration {
	var out []time.Duration
	for n := 1; n <= attempts; n++ {
		out = append(out, Delay(n, base, max))
	}
	return out
}
