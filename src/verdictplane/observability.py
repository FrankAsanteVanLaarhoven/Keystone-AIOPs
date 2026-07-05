"""VerdictPlane — observability export (OFF the enforcement path).

Maps tamper-evident ledger entries to OpenTelemetry-style log records for a SIEM / OTel collector.
This module is deliberately **NON-ENFORCEMENT**: the enforcement path (interceptor / policy / gate /
provenance) never imports it — proven statically in `tests/test_enforcement_imports.py`. Consequences:

  * an exporter failure can never affect a governance decision (it is unreachable from `govern()`), and
  * enforcement stays zero-egress — this module performs **no network I/O** itself; transmission is a
    caller-injected `sink`. By default `export()` just builds and returns the records (no egress).

CLI: `python -m verdictplane.observability <ledger.jsonl>` prints the OTel records.
"""

from __future__ import annotations

import json
import sys
from typing import Callable, Iterable, Optional

RESOURCE = {"service.name": "verdictplane", "telemetry.sdk.name": "verdictplane-observability"}


def _rule_id(rule) -> Optional[str]:
    if rule is None:
        return None
    return json.dumps(rule, sort_keys=True, default=str)


def to_otel(entries: Iterable[dict]) -> list[dict]:
    """Ledger entries (`{ts, prev, record, hash}`) -> OTel-style log records (deterministic)."""
    out = []
    for e in entries:
        rec = e.get("record", {}) or {}
        action = rec.get("action", {}) or {}
        out.append({
            "resource": dict(RESOURCE),
            "timeUnixNano": e.get("ts"),
            "severityText": "INFO",
            "body": f"{action.get('tool')} -> {rec.get('decision')}/{rec.get('outcome')}",
            "attributes": {
                "governance.tool": action.get("tool"),
                "governance.agent": action.get("agent"),
                "governance.effect": action.get("effect"),
                "governance.decision": rec.get("decision"),
                "governance.outcome": rec.get("outcome"),
                "governance.rule": _rule_id(rec.get("rule")),
                "ledger.hash": e.get("hash"),
            },
        })
    return out


def export(entries: Iterable[dict], sink: Optional[Callable[[list], None]] = None) -> list[dict]:
    """Build OTel records and hand them to `sink` (default None -> no egress); return the records.

    A failing `sink` raises HERE — off the enforcement path — so it can never touch `govern()`.
    """
    records = to_otel(entries)
    if sink is not None:
        sink(records)
    return records


def main(argv: list) -> int:
    import argparse

    from verdictplane.provenance import Ledger  # local import: keep module import-light

    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    a = ap.parse_args(argv)
    print(json.dumps(export(Ledger(a.ledger).entries()), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
