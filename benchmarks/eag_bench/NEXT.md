# EAG-Bench — Phase B handoff / next milestone

Checkpoint for a fresh session. Everything below is committed on `main`.

## Done (Phase B, four tracks — all in `make test`, 224 tests)

| track | command | result | honest scope |
| --- | --- | --- | --- |
| Case schema + validator | `make eag-validate` | 100/100 valid | stdlib-only; verdict↔sentinel guards |
| Single-action corpus | `make enterprise-bench` | **0/100 escapes**, verdict 100/100 | synthetic breadth, one host, not externally validated |
| Agentic red-team | `make redteam-bench` | **8/8 defeated · 7/7 boundary** | 2 buckets; does NOT claim unbreakability |
| Compliance compiler | `make compliance-report` | 115 cases → per-framework matrices | **coverage, not certification** (disclaimed) |

## Next major milestone — real / anonymized traces (the credibility lever)

The `source: real | anonymized` field and `provenance` block already exist; the harness is
**source-agnostic**, so real cases flow through the same 0-escape check — no harness change needed.
The work is *safe ingestion*, not new evaluation logic.

**Safety rail — ✅ SHIPPED** (`benchmarks/eag_bench/deid.py`, `tests/test_deid.py`, 230 tests):
- de-identify reuses `verdictplane.interceptor.redact` (masks secret-named keys) + PII pattern scrub
  (email, IPv4, SSN, card, AWS key, private key, JWT) on carrier fields.
- **hard gate:** re-scans the WHOLE record; any residual secret/PII → the ingest CLI **rejects**
  (non-zero exit, no file written), and output is force-tagged `source: anonymized` (never `real`).
  CLI: `python benchmarks/eag_bench/deid.py <in.json ...> --out <dir>`.

**Next: Wave-1 ingestion** — map ToolBench/WebArena trajectories → action cases, run each through
`deid.py`, schema-validate, then `make enterprise-bench` (harness is source-agnostic). Verify each
dataset's licence at ingest.

**Then:** small `provenance` additions (`origin`, `deid_method`, `license`); a de-identification
checklist (strip secrets/PII, tokenise identifiers, drop free-text, verify no real credentials,
confirm licence/consent, record `deid_method`); source only permissively-licensed or self-owned logs.

**Risks:** PII leakage (→ the scan test), licensing/consent, and over-claiming "real" for lightly-
anonymised synthetic (→ keep `source` honest; `anonymized` ≠ `real`).

## Alternative / parallel — EIGS-100 scoring

Lower-risk quick win: aggregate the *already-measured* numbers into the 8-track weighted rubric
(enforcement correctness, side-effect escape, tamper, red-team, zero-egress, compliance coverage,
performance, workflow). Mostly wiring, no new data. **Caveat:** a headline score on a synthetic corpus
must be scoped as such until real traces + external repro exist.

## Recommended order

**Real traces first** (biggest credibility lever), starting with the de-id safety rail. Do EIGS-100
after, so the headline score reflects a partly-real corpus rather than a purely synthetic one.

## Sourcing plan (decided)

**Wave 1 — public, licence-clean agent/tool-use datasets** (build the pipeline + privacy gate here):
prioritise **ToolBench/ToolEval** and **WebArena** (further candidates: GAIA, AgentBench). Extract
consequential actions from the trajectories → action cases tagged `source: anonymized`.
- **Verify each dataset's licence at ingest — do NOT assume "open".** Record it in `provenance.license`.

**Wave 2 (later)** — self-owned / consented logs (VerdictPlane / DriftGuard / Sentinel usage; pilot
data with explicit consent). Higher credibility; only after the de-id gate is proven on public data.

**Honest scope caveat (important):** these datasets supply real *action distributions / shapes*, not
real enterprise *governance decisions* — the `expected_verdict` stays policy-derived. So the upgrade is
"real actions, synthetic labels", tagged `source: anonymized` (never `real`); do not claim "real
governance data".

## Still open for the next session
- Target size of the first anonymized batch (keep small; provenance/quality over volume).
- EIGS-100 weights — adopt the roadmap's or revisit.
