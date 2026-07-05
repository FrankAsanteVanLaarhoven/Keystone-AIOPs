"""EAG-Bench de-identification safety rail. The gate must scrub carrier fields, force
source=anonymized, and REJECT (not warn) any record with residual secret/PII."""

import glob
import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EAG = os.path.join(ROOT, "benchmarks", "eag_bench")


def _load():
    spec = importlib.util.spec_from_file_location("eag_deid", os.path.join(EAG, "deid.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


D = _load()


def _case(**over):
    c = {"case_id": "x.y.z", "action": {"tool": "t", "effect_type": "read", "arguments": {}},
         "source": "anonymized"}
    c.update(over)
    return c


def test_scan_detects_common_pii():
    kinds = {k for _, k, _ in D.scan_case(_case(action={
        "tool": "t", "effect_type": "read",
        "arguments": {"email": "a@b.com", "ip": "10.1.2.3", "ssn": "123-45-6789"}}))}
    assert {"email", "ipv4", "ssn"} <= kinds


def test_deidentify_scrubs_carrier_fields_and_passes_gate():
    raw = _case(action={"tool": "payments", "effect_type": "payment",
                        "arguments": {"payee": "a@b.com", "memo": "src ip 10.0.0.1"}},
                description="contact j@x.com if needed")
    ok, clean, residual = D.ingest(raw)
    assert ok and residual == []
    assert clean["source"] == "anonymized"
    blob = json.dumps(clean)
    assert "a@b.com" not in blob and "10.0.0.1" not in blob and "j@x.com" not in blob


def test_gate_rejects_pii_in_unexpected_field():
    ok, _clean, residual = D.ingest(_case(evaluation_tags=["ok", "reach me at leak@corp.com"]))
    assert not ok
    assert any(k == "email" for _, k, _ in residual)


def test_gate_rejects_unmasked_secret_key():
    ok, _clean, residual = D.ingest(_case(provenance={"api_key": "AKIAIOSFODNN7EXAMPLE"}))
    assert not ok
    assert residual


def test_secret_named_arg_is_masked_and_passes():
    ok, clean, residual = D.ingest(_case(action={
        "tool": "t", "effect_type": "write", "arguments": {"password": "hunter2"}}))
    assert ok and residual == []
    assert clean["action"]["arguments"]["password"] == "[REDACTED]"


def test_existing_nonsynthetic_cases_pass_the_gate():
    for d in ("cases", os.path.join("redteam", "cases")):
        for f in glob.glob(os.path.join(EAG, d, "*.json")):
            c = json.load(open(f))
            if c.get("source") != "synthetic":
                ok, _clean, residual = D.ingest(c)
                assert ok, (f, residual)
