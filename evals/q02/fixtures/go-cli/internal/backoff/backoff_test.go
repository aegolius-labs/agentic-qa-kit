package backoff

import (
	"testing"
	"time"
)

func TestDelayDoubles(t *testing.T) {
	cases := map[int]time.Duration{1: 100 * time.Millisecond, 2: 200 * time.Millisecond, 3: 400 * time.Millisecond}
	for n, want := range cases {
		if got := Delay(n, 100*time.Millisecond, time.Second); got != want {
			t.Errorf("Delay(%d) = %v, want %v", n, got, want)
		}
	}
}

func TestDelayIsCapped(t *testing.T) {
	if got := Delay(10, 100*time.Millisecond, time.Second); got != time.Second {
		t.Errorf("Delay(10) = %v, want 1s", got)
	}
}
