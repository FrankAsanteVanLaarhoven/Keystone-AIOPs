# VerdictPlane — Benchmark Report (P5)

Produced by `make bench` (bench/run_bench.py) from live measurement.
Machine-readable source: `artifacts/stats.json` (regenerated, not committed).

- **Commit:** `bd456d2e2ee655900c1cd9f5a49565db33f7ddca (working tree DIRTY at capture time)`
- **Captured:** 2026-07-03T10:49:50Z
- **Host:** Intel(R) Core(TM) i7-14700K · Python 3.13.13 · Linux-6.8.0-111-generic-x86_64-with-glibc2.35
- **Ledger:** filesystem `ext4`, fsync=False
- **Advisory:** off (forced); enforcement never imports advisory regardless
- **Method:** 5 independent runs x 20000 allow-path calls
  (fresh ledger per run, 500-call warmup before throughput window); median run shown.

## Targets scoreboard

| Target | Result |
| --- | --- |
| Allow-path p99 < 1 ms (every run) | PASS — worst run 20.85 µs |
| Throughput > 10k governed actions/s (worst run) | PASS — worst run 61004/s |
| Tamper detection 100% at exact index | PASS — 200/200 |
| Zero provenance gaps + chain verifies | PASS — 0 gaps / 200 calls |
| Fail-safe with advisory forced broken | PASS |
| Reproducibility (allow p99 spread <= 10%) | FAIL — spread 11.7% |

## Enforcement latency (median run, µs)

| Path | p50 | p95 | p99 |
| --- | --- | --- | --- |
| raw call (baseline) | 0.03 | 0.03 | 0.05 |
| governed allow | 16.05 | 17.32 | 19.0 |
| governed deny | 18.48 | 19.96 | 21.43 |
| require_human (auto-resolved gate) | 100.72 | 124.36 | 223.33 |
| ledger append | 10.59 | 11.48 | 12.79 |

Full-chain verify: 31000 entries in 0.1568 s.

## Stability across runs

- allow p99 per run (µs): [18.62, 19.41, 19.0, 18.87, 20.85] — spread 11.7%
- throughput per run (ops/s): [61787, 62710, 61004, 61582, 61693] — spread 2.8%

## Real workloads under load (P4 wrappers, workloads.yaml policy)

| Path | p50 | p95 | p99 |
| --- | --- | --- | --- |
| DriftGuard promote (Staging, allow) | 25.23 | 27.52 | 35.78 |
| DriftGuard promote (Production, gated+auto-resolve) | 122.71 | 143.56 | 259.14 |
| Sentinel proposal (recorded) | 24.17 | 26.04 | 29.5 |

- Staging-promote throughput: 38557 ops/s
- Chain verifies after load: True

## Fail-safe detail

Advisory backend configured and transport forced to error: summary returned =
`None`; policy decisions unchanged =
True; unmatched action default =
`require_human`.

## Caveats

- Human-gated paths are human-scale by design; the auto-resolved gate number
  measures VerdictPlane's machinery (submit + resolve + 2 ledger appends), not
  reviewer latency.
- Numbers are host- and filesystem-dependent; re-run `make bench` on the
  target machine. fsync=False (default): tamper evidence is unaffected, a
  crash can lose the buffered tail (truncation is detectable via an anchored
  head). CPU frequency scaling is the main variance source.
