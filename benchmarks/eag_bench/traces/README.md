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

## `sentinel_incidents.jsonl`

Source: Sentinel-AIOPs (self-owned; `/home/favl/Sentinel-AIOPs`), which is built on the same contract —
*Sentinel proposes, VerdictPlane governs*. Generated through Sentinel's **own** code:
`action_proposal.build_action_proposal(<flag_spike incident>)` → `verdictplane.proposal_to_action(...)`
(not hand-authored). The `flag_spike` incident (a checkout deploy spiking p95 120→940ms) is Sentinel's
canonical investigation fixture.

- proposal `rollback_change` → VerdictPlane action `incident.rollback` / `execute` (checkout,
  `deploy checkout@v128`, confidence 0.91, grounding 1.0). No PII/secrets.

### Result

```
replayed 1/1 real action — verdict distribution {require_human: 1} — escapes 0
```

VerdictPlane routes the remediation to **human approval** — consistent with the cross-layer story: a
consequential mutation (rollback) is not auto-executed. A second real system + a second domain
(incident remediation, not just model promotion).

## Honest scope (both traces)

Small — **3 real actions across 2 self-owned systems (DriftGuard, Sentinel) and 2 domains**, all routed
to `require_human`, 0 escapes. A genuine early real signal, **not** a corpus. The Sentinel entry uses
its canonical `flag_spike` fixture (1 action); *richer* Sentinel data (fresh causal RCA over the
RCAEval RE1 / SMD benchmarks in `Sentinel-AIOPs/engine/artifacts/`) needs its heavier pipeline — a
bounded follow-up. Locked into `make test` (`tests/test_replay.py`) so the real results stay
reproducible; surfaced (unscored) in the EIGS scoreboard.
