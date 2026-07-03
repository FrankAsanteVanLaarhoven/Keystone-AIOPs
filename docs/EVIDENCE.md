# VerdictPlane — Evidence Pack (P0–P4)

Assembled from live runs by `make evidence` (scripts/build_evidence.py).
Nothing below is hand-written output.

- **Commit:** `bd456d2e2ee655900c1cd9f5a49565db33f7ddca`
- **Repo:** https://github.com/FrankAsanteVanLaarhoven/VerdictPlane
- **Reproduce:** `make setup && make test && make evidence`

## Evidence Matrix

| Claim | Evidence | Result |
| --- | --- | --- |
| Enforcement path is deterministic (no model/network import) | E2 — static AST allowlist test output | 0 violations |
| Advisory cannot affect decisions | E2 — `test_enforcement_never_imports_advisory_or_cli` per module | 0 imports |
| Human approval blocks execution | E4 — before/after transcript: side effect absent until CLI approve; deny/timeout leave it absent | 100% gated |
| Failed baseline gate can never ship | E4 case C — deterministic `PolicyDenied`, no approval requested | fail-closed |
| Ledger is tamper-evident | E3 battery + E6 live forgery pinpointed at exact line | 100% detected |
| Provenance completeness | E5 — one terminal record per governed call, chain verifies clean | 0 gaps |
| P4 workloads governed end-to-end | E1 + E4/E5 — DriftGuard promote + Sentinel rollback through the gate | pass |
| Zero egress during enforcement | E7 — socket kill-switch + empty-netns battery (kernel-level) | pass |


## E1 — Full test suite

```
........................................................................ [ 80%]
....................................                                     [100%]
180 passed in 2.79s
```

Recent history:

```
bd456d2 Bench: spread target gated locally, informational on shared runners
22bd83c Rename project to VerdictPlane; add evidence appendix
ad4fc02 Fix gate write race caught by CI: atomic pending/resolved writes
e525ef0 CI gating + PyPI-ready packaging (post-P7 hardening)
144e3f8 P7 OSS polish: README quickstart, architecture + case study docs, MIT license
6d1ac86 Evidence pack: clean capture including E7
```


## E2 — Enforcement-path import guard (static, per module)

```
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[__init__.py] PASSED [  4%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[gate.py] PASSED [  9%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[interceptor.py] PASSED [ 13%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[mcp.py] PASSED [ 18%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[policy.py] PASSED [ 22%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[provenance.py] PASSED [ 27%]
tests/test_enforcement_imports.py::test_enforcement_imports_allowlisted[types.py] PASSED [ 31%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[__init__.py] PASSED [ 36%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[gate.py] PASSED [ 40%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[interceptor.py] PASSED [ 45%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[mcp.py] PASSED [ 50%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[policy.py] PASSED [ 54%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[provenance.py] PASSED [ 59%]
tests/test_enforcement_imports.py::test_no_network_or_model_clients[types.py] PASSED [ 63%]
tests/test_enforcement_imports.py::test_enforcement_set_is_not_empty PASSED [ 68%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[__init__.py] PASSED [ 72%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[gate.py] PASSED [ 77%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[interceptor.py] PASSED [ 81%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[mcp.py] PASSED [ 86%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[policy.py] PASSED [ 90%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[provenance.py] PASSED [ 95%]
tests/test_enforcement_imports.py::test_enforcement_never_imports_advisory_or_cli[types.py] PASSED [100%]
============================== 22 passed in 0.02s ==============================
```


## E3 — Tamper-detection battery (exact-index localization)

```
tests/test_provenance.py::test_empty_ledger_verifies PASSED              [  2%]
tests/test_provenance.py::test_intact_chain_verifies PASSED              [  4%]
tests/test_provenance.py::test_head_survives_reload PASSED               [  7%]
tests/test_provenance.py::test_append_returns_head_hash PASSED           [  9%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[0] PASSED [ 11%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[1] PASSED [ 14%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[2] PASSED [ 16%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[3] PASSED [ 19%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[4] PASSED [ 21%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[5] PASSED [ 23%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[6] PASSED [ 26%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[7] PASSED [ 28%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[8] PASSED [ 30%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[9] PASSED [ 33%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[10] PASSED [ 35%]
tests/test_provenance.py::test_random_line_mutation_detected_at_exact_index[11] PASSED [ 38%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[0] PASSED [ 40%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[1] PASSED [ 42%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[2] PASSED [ 45%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[3] PASSED [ 47%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[4] PASSED [ 50%]
tests/test_provenance.py::test_hash_fixed_mutation_detected_downstream[5] PASSED [ 52%]
tests/test_provenance.py::test_deleted_middle_line_detected[0] PASSED    [ 54%]
tests/test_provenance.py::test_deleted_middle_line_detected[1] PASSED    [ 57%]
tests/test_provenance.py::test_deleted_middle_line_detected[2] PASSED    [ 59%]
tests/test_provenance.py::test_deleted_middle_line_detected[3] PASSED    [ 61%]
tests/test_provenance.py::test_deleted_middle_line_detected[4] PASSED    [ 64%]
tests/test_provenance.py::test_deleted_middle_line_detected[5] PASSED    [ 66%]
tests/test_provenance.py::test_inserted_forged_line_detected[0] PASSED   [ 69%]
tests/test_provenance.py::test_inserted_forged_line_detected[1] PASSED   [ 71%]
tests/test_provenance.py::test_inserted_forged_line_detected[2] PASSED   [ 73%]
tests/test_provenance.py::test_inserted_forged_line_detected[3] PASSED   [ 76%]
tests/test_provenance.py::test_inserted_forged_line_detected[4] PASSED   [ 78%]
tests/test_provenance.py::test_inserted_forged_line_detected[5] PASSED   [ 80%]
tests/test_provenance.py::test_reordered_lines_detected[0] PASSED        [ 83%]
tests/test_provenance.py::test_reordered_lines_detected[1] PASSED        [ 85%]
tests/test_provenance.py::test_reordered_lines_detected[2] PASSED        [ 88%]
tests/test_provenance.py::test_reordered_lines_detected[3] PASSED        [ 90%]
tests/test_provenance.py::test_reordered_lines_detected[4] PASSED        [ 92%]
tests/test_provenance.py::test_reordered_lines_detected[5] PASSED        [ 95%]
tests/test_provenance.py::test_garbage_line_detected PASSED              [ 97%]
tests/test_provenance.py::test_tail_truncation_detected_via_anchored_head PASSED [100%]
============================== 42 passed in 0.12s ==============================
```


## E4 — Live gate demo: DriftGuard promote + Sentinel rollback (cross-process, via the reviewer CLI)

```
$ # governed_promote('7', gate_passed) is now BLOCKED in another process

$ test -f registry.json && echo exists || echo absent
absent   <- side effect has NOT run

$ verdictplane pending
9bcbbb9ad2d8c69f  model.promote  effect=promote  agent=driftguard  age=0s
  args: {"baseline": {"baseline_macro_f1": 0.85, "candidate_macro_f1": 0.91, "margin": 0.02, "passed": true, "reason": null}, "stage": "Production", "version": "7"}

$ verdictplane approve 9bcbbb9ad2d8 --by frank
approved 9bcbbb9ad2d8c69f (model.promote) by frank

$ cat registry.json
{"production_alias": "7"}   <- side effect ran ONLY after approval

$ verdictplane deny efc933e3df24 --by frank
denied efc933e3df24f0b8 (model.promote) by frank

$ cat registry.json
{"production_alias": "7"}   <- unchanged; caller got ApprovalDenied

# governed_promote('9', gate_FAILED) -> PolicyDenied: model.promote: denied by policy
# (deterministic policy deny; no approval was ever requested)

$ verdictplane approve 15740a293243 --by frank   # Sentinel rollback
approved 15740a2932436f96 (incident.rollback) by frank

# rollback executed with incident payload: {'service': 'productcatalog', 'change': 'deploy v2.3.1', 'detect_t': 34}
```


## E5 — Resulting provenance ledger

`verdictplane log`:

```
9bcbbb9ad2d8c69f  pending          require_human  model.promote  agent=driftguard
a9172a72364b5bb4  executed         require_human  model.promote  agent=driftguard
efc933e3df24f0b8  pending          require_human  model.promote  agent=driftguard
8fc2b4e450efcede  denied_by_human  require_human  model.promote  agent=driftguard
8155c9008b8f0566  blocked          deny           model.promote  agent=driftguard
877027b28150fc46  executed         allow          incident.propose  agent=sentinel
15740a2932436f96  pending          require_human  incident.rollback  agent=sentinel
647ddbba4e0a62c2  executed         require_human  incident.rollback  agent=sentinel
```

`verdictplane verify`:

```
ledger ok (8 entries, head=647ddbba4e0a62c2)
```

Raw hash-chained records (first 2 of 8):

```json
{"hash": "9bcbbb9ad2d8c69fc24376f8e9e60e8ab0a1208fc644aaed08746e83ec62e8ef", "prev": "0000000000000000000000000000000000000000000000000000000000000000", "record": {"action": {"agent": "driftguard", "args": {"baseline": {"baseline_macro_f1": 0.85, "candidate_macro_f1": 0.91, "margin": 0.02, "passed": true, "reason": null}, "stage": "Production", "version": "7"}, "context": {}, "effect": "promote", "tool": "model.promote"}, "decision": "require_human", "outcome": "pending", "rule": {"decision": "require_human", "match": {"args.baseline.passed": true, "args.stage": "Production", "tool": "model.promote"}}}, "ts": 1783075782588283397}
{"hash": "a9172a72364b5bb4049a2ecacdba27ba451ca47775d39cd1b8ed2b17caa60869", "prev": "9bcbbb9ad2d8c69fc24376f8e9e60e8ab0a1208fc644aaed08746e83ec62e8ef", "record": {"action": {"agent": "driftguard", "args": {"baseline": {"baseline_macro_f1": 0.85, "candidate_macro_f1": 0.91, "margin": 0.02, "passed": true, "reason": null}, "stage": "Production", "version": "7"}, "context": {}, "effect": "promote", "tool": "model.promote"}, "decision": "require_human", "outcome": "executed", "rule": {"decision": "require_human", "match": {"args.baseline.passed": true, "args.stage": "Production", "tool": "model.promote"}}, "token": "9bcbbb9ad2d8c69fc24376f8e9e60e8ab0a1208fc644aaed08746e83ec62e8ef"}, "ts": 1783075782749355224}
```


## E6 — Live forgery detection

```
$ verdictplane verify   # after forging line 3's outcome
LEDGER TAMPERED at line 3
exit code: 1
```


## E7 — Zero egress during enforcement

Full enforcement battery (all decision paths, gate resolution, both P4
workloads, chain verify) under a socket kill-switch and again inside an empty
network namespace (`unshare -rn`; outbound probe must fail before the battery
runs):

```
tests/test_zero_egress.py::test_enforcement_runs_with_sockets_disabled PASSED [ 50%]
tests/test_zero_egress.py::test_enforcement_runs_in_empty_network_namespace PASSED [100%]
============================== 2 passed in 0.28s ===============================
```

The sidecar deployment (deploy/sidecar-compose.yml) additionally runs both
containers with `network_mode: "none"` — the container runtime allocates no
interfaces at all, so no-egress holds by construction in deployment too.

## Governing policy (policies/workloads.yaml)

```yaml
# Policy for the first two governed workloads (P4).
# First-match wins; anything unmatched falls to the safe default.

default: require_human

rules:
  # DriftGuard — fail-closed: a candidate that failed the baseline gate can
  # never ship, no matter who asks. Deterministic deny, no human needed.
  - match: { tool: model.promote, args.baseline.passed: false }
    decision: deny

  # Production promotion always needs a human, even with a passing gate.
  - match: { tool: model.promote, args.stage: Production, args.baseline.passed: true }
    decision: require_human

  # Staging promotions with a passing gate flow unattended (canary-style).
  - match: { tool: model.promote, args.stage: Staging, args.baseline.passed: true }
    decision: allow

  # Sentinel — recording an assistive proposal is safe and always audited.
  - match: { tool: incident.propose, effect: propose }
    decision: allow

  # Executing a proposed rollback is a real side effect: human required.
  - match: { tool: incident.rollback }
    decision: require_human
```

