# Keystone — Benchmark Report (P5)

Produced by `make bench` (bench/run_bench.py) from live measurement.
Machine-readable source: `artifacts/stats.json` (regenerated, not committed).

- **Commit:** `b8ad473dac7c610e19aa1a8d5095c60ca76b3b71`
- **Captured:** 2026-07-03T00:43:18Z
- **Host:** Intel(R) Core(TM) i7-14700K · Python 3.13.13 · Linux-6.8.0-111-generic-x86_64-with-glibc2.35
- **Ledger:** filesystem `ext4`, fsync=False
- **Advisory:** off (forced); enforcement never imports advisory regardless
- **Method:** 5 independent runs x 20000 allow-path calls
  (fresh ledger per run, 500-call warmup before throughput window); median run shown.

## Targets scoreboard

| Target | Result |
| --- | --- |
| Allow-path p99 < 1 ms (every run) | PASS — worst run 18.93 µs |
| Throughput > 10k governed actions/s (worst run) | PASS — worst run 61658/s |
| Tamper detection 100% at exact index | PASS — 200/200 |
| Zero provenance gaps + chain verifies | PASS — 0 gaps / 200 calls |
| Fail-safe with advisory forced broken | PASS |
| Reproducibility (allow p99 spread <= 10%) | PASS — spread 3.8% |

## Enforcement latency (median run, µs)

| Path | p50 | p95 | p99 |
| --- | --- | --- | --- |
| raw call (baseline) | 0.03 | 0.05 | 0.05 |
| governed allow | 16.1 | 17.47 | 18.63 |
| governed deny | 18.59 | 20.17 | 21.43 |
| require_human (auto-resolved gate) | 88.43 | 108.42 | 208.19 |
| ledger append | 10.57 | 11.55 | 12.69 |

Full-chain verify: 31000 entries in 0.1535 s.

## Stability across runs

- allow p99 per run (µs): [18.93, 18.41, 18.23, 18.66, 18.63] — spread 3.8%
- throughput per run (ops/s): [61803, 62179, 62037, 61658, 62157] — spread 0.8%

## Real workloads under load (P4 wrappers, workloads.yaml policy)

| Path | p50 | p95 | p99 |
| --- | --- | --- | --- |
| DriftGuard promote (Staging, allow) | 25.16 | 26.99 | 30.13 |
| DriftGuard promote (Production, gated+auto-resolve) | 111.0 | 137.14 | 245.08 |
| Sentinel proposal (recorded) | 23.91 | 25.64 | 28.07 |

- Staging-promote throughput: 38529 ops/s
- Chain verifies after load: True

## Fail-safe detail

Advisory backend configured and transport forced to error: summary returned =
`None`; policy decisions unchanged =
True; unmatched action default =
`require_human`.

## Caveats

- Human-gated paths are human-scale by design; the auto-resolved gate number
  measures Keystone's machinery (submit + resolve + 2 ledger appends), not
  reviewer latency.
- Numbers are host- and filesystem-dependent; re-run `make bench` on the
  target machine. fsync=False (default): tamper evidence is unaffected, a
  crash can lose the buffered tail (truncation is detectable via an anchored
  head). CPU frequency scaling is the main variance source.
