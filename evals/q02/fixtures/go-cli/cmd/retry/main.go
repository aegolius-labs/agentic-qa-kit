package main

import (
	"flag"
	"fmt"
	"os"
	"os/exec"
	"time"

	"example.com/retry/internal/backoff"
)

func main() {
	attempts := flag.Int("attempts", 3, "maximum number of runs")
	base := flag.Duration("base", 200*time.Millisecond, "first delay")
	max := flag.Duration("max", 5*time.Second, "delay cap")
	flag.Parse()
	args := flag.Args()
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "usage: retry [flags] -- command [args...]")
		os.Exit(2)
	}
	delays := backoff.Schedule(*attempts, *base, *max)
	for i := 0; i < *attempts; i++ {
		cmd := exec.Command(args[0], args[1:]...)
		cmd.Stdout, cmd.Stderr = os.Stdout, os.Stderr
		if err := cmd.Run(); err == nil {
			return
		}
		if i < len(delays) {
			time.Sleep(delays[i])
		}
	}
	os.Exit(1)
}
