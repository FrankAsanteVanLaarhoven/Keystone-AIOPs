# EAG-Bench — Seed Corpus Coverage Matrix (v1.0, 100 cases)

The seed Enterprise Action Corpus: **100 cases, exactly 10 per domain**. Every case validates against
[`schema/action_case.schema.json`](schema/action_case.schema.json) (`make eag-validate`), and all 100
are driven through the real `govern()` choke point by the escape harness (`make enterprise-bench`).
Both run in `make test`.

**Verdicts:** 34 allow · 12 allow_after_approval · 25 require_human · 20 deny · 6 deny_after_timeout ·
3 deny_after_veto = **100**. **Adversarial:** 21 (with `attack_annotations`). Every domain carries all
of: reads (allow), gated writes (require_human / allow_after_approval), and hard denies.

## Per-domain coverage (10 each)

| domain | allow | require_human | allow_after_approval | deny | timeout | veto |
| --- | --- | --- | --- | --- | --- | --- |
| cloud_iam | 3 | 2 | 2 | 3 | – | – |
| model_promotion | 2 | 2 | 1 | 3 | 1 | 1 |
| incident_rollback | 3 | 2 | 1 | – | 3 | 1 |
| mcp_write_tool | 3 | 3 | 1 | 3 | – | – |
| data_export_pii | 3 | 2 | 1 | 3 | 1 | – |
| security_response | 3 | 2 | 1 | 4 | – | – |
| finance_payment | 3 | 2 | 2 | 2 | – | 1 |
| code_deployment | 3 | 1 | 1 | 2 | 1 | 1 |
| hr_employee_data | 3 | 4 | 1 | 2 | – | – |
| robotics_ot | 3 | 3 | 1 | 3 | – | – |

*(Counts are indicative — the authoritative source is `cases/*.json`, verified by the harness.)*

## Coverage guarantees (why this set)

- **Every verdict type** appears, including the three *resolved* outcomes the escape harness must
  exercise (`allow_after_approval`, `deny_after_timeout`, `deny_after_veto`).
- **Positive governance** (`allow_after_approval`) spans a single-approver window (`after_approval`)
  and quorum windows (`after_quorum`) — different gate outcomes, not one shape repeated.
- **The 0-escape metric** is checkable per case: `never` (nothing may fire), `read_only`
  (no mutation), `after_allow`, `after_approval`, `after_quorum`.
- **21 adversarial cases** carry `attack_annotations` (priv-esc, traversal, exfiltration, supply-chain,
  fraud, defense-evasion, safety-override, change-freeze, DoS).
- **Negative controls** on the seed cases flip the dangerous attribute so a case cannot pass trivially.

## Deferred to v1.1 (surfaced while authoring, out of scope for v0.2)

- **Multiple sentinels per case** — compound actions are one-effect-per-case for now.
- **First-class `context` block** — preconditions (change-freeze, MFA, out-of-hours) currently ride
  in `arguments` (`Action` already has a `context` field to receive them).
- **Sentinel `kind: config_change`** — EDR/security-control flips are tagged `config_change` and
  mapped to `deploy_flag` today.

## Result (Side-Effect Escape harness)

`make enterprise-bench` drives all 100 cases through the real `govern()` choke point under
[`policies/eag_bench.yaml`](policies/eag_bench.yaml), replacing each side effect with an instrumented
sink and applying the gate resolution the case calls for (approve k / veto / timeout / none):

```
unapproved side-effect escapes : 0 / 100   (target 0)
verdict correctness            : 100 / 100
ledger completeness            : 100 / 100
positive-path executions       : 100 / 100
ledger chain intact            : 100 / 100
```

**Scope (honest):** a synthetic 100-case seed corpus on one host — a reproducible standard, not yet an
externally-validated SOTA number, and its weight is breadth of coverage, not independent provenance.
The result re-runs from `make enterprise-bench` and is guarded in CI by `tests/test_eag_harness.py`,
which also asserts the metric is **non-vacuous** (a permissive allow-everything policy makes the
harness report escapes).

## Next

Grow toward EAG-Bench scale with **real / anonymized traces** (the `source` field is ready) and
independent validation, then the remaining tracks (agentic red-team, compliance compiler, OTel export)
and EIGS-100 scoring.
