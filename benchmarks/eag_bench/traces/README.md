# EAG-Bench — self-owned real traces

Real governed-action traces from the author's own systems, replayed through VerdictPlane under the
EAG-Bench policy. These are **not** synthetic benchmark cases — they are actual decisions captured from
real measured runs. The trace supplies real **action shapes**; the verdicts are **policy-derived**
(see [`../NEXT.md`](../NEXT.md) for the honest boundary). No case scaffolding is fabricated.

## `driftguard_promotions.jsonl`

Source: DriftGuard measured runs (self-owned; `driftguard/artifacts/`).

- **ag_news primary text classifier** (seed 42) — `deployment_report.md`, 2026-07-01. DriftGuard's ML
  promotion gate: **PASS** (macro-F1 0.9197 ≥ baseline 0.8956), registered v4, promoted to prod.
- **distilbert-base-uncased** transformer — `metrics_transformer.json`, 2026-07-02. DriftGuard's ML
  gate: **PASS** (macro-F1 0.9412 ≥ incumbent 0.9197), promoted to prod.

No PII/secrets (model names, macro-F1s, dates) — passes the de-id gate unmodified.

### Result (`python benchmarks/eag_bench/replay.py traces/driftguard_promotions.jsonl`)

```
replayed 2/2 real actions (0 rejected by privacy gate, 0 malformed)
verdict distribution: {require_human: 2}
allow executed: 0 | unapproved side-effect escapes: 0
```

**Two independent governance layers.** DriftGuard's *ML* gate passed both on model quality.
VerdictPlane's *enterprise action* policy independently routes production model-promotions to
**dual-control human approval** (require_human, quorum 2) — quality-passing is not authority-to-ship.
Zero unapproved side effects. This reports real action shapes + policy-derived verdicts; it does not
claim DriftGuard's gate "should" have decided differently.

### Honest scope

Small (2 real decisions) and single-domain (model promotion) — a genuine first real-data point, **not**
a corpus. Grow it as more self-owned governed actions accrue (further DriftGuard runs, Sentinel logs,
real VerdictPlane deployments). Locked into `make test` (`tests/test_replay.py`) so the real result
stays reproducible.
