"""VerdictPlane observability export (T9). Real governance events round-trip to OTel records, and a
failing exporter sink cannot touch the enforcement path (which never imports this module — see
tests/test_enforcement_imports.py)."""

import os
import tempfile

import pytest

from verdictplane import observability as O
from verdictplane.gate import Gate
from verdictplane.interceptor import PolicyDenied, govern
from verdictplane.provenance import Ledger


def _ledger_with_real_events(tmp):
    led = Ledger(os.path.join(tmp, "l.jsonl"))
    gate = Gate(os.path.join(tmp, "gate"), poll_interval=0.01)
    policy = {"default": "allow", "rules": [{"match": {"tool": "danger"}, "decision": "deny"}]}
    govern({"tool": "safe", "effect": "read", "args": {}, "agent": "a"}, lambda: "ok",
           policy=policy, ledger=led, gate=gate)
    try:
        govern({"tool": "danger", "effect": "delete", "args": {}, "agent": "a"}, lambda: "ok",
               policy=policy, ledger=led, gate=gate)
    except PolicyDenied:
        pass
    return led


def test_governance_events_round_trip_to_otel():
    with tempfile.TemporaryDirectory() as tmp:
        led = _ledger_with_real_events(tmp)
        recs = O.to_otel(led.entries())
    assert len(recs) == 2
    by_tool = {r["attributes"]["governance.tool"]: r for r in recs}
    assert by_tool["safe"]["attributes"]["governance.outcome"] == "executed"
    danger = by_tool["danger"]["attributes"]
    assert danger["governance.decision"] == "deny" and danger["governance.outcome"] == "blocked"
    assert all(r["resource"]["service.name"] == "verdictplane" for r in recs)
    assert all(r["attributes"]["ledger.hash"] for r in recs)  # provenance linkage carried


def test_export_returns_records_and_no_egress_by_default():
    entries = [{"ts": 1, "record": {"action": {"tool": "t", "agent": "x"}, "decision": "allow",
                                    "outcome": "executed"}, "hash": "h"}]
    recs = O.export(entries)  # no sink -> no network
    assert recs[0]["attributes"]["governance.tool"] == "t"


def test_failing_sink_raises_in_exporter_not_enforcement():
    entries = [{"ts": 1, "record": {"action": {"tool": "t"}, "decision": "allow",
                                    "outcome": "executed"}, "hash": "h"}]

    def bad(_recs):
        raise RuntimeError("collector down")

    with pytest.raises(RuntimeError):
        O.export(entries, sink=bad)
    # records still build independently of any sink failure (the sink is the only egress point)
    assert O.export(entries)[0]["attributes"]["governance.tool"] == "t"
