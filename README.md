# Keystone

In-path, zero-egress control plane for AI actions: every consequential
agent/tool action is **recorded** (tamper-evident hash-chained ledger),
**checked** against declarative policy **before** it commits (deterministic —
no model in the enforcement path), and **gated** by a human when it matters
(default-deny posture: unmatched actions require approval).

Status: phased build in progress (P0 trust core ✅). Full docs land in P7.

```bash
make setup   # venv + editable install
make test    # conformance + tamper-detection suites
```
