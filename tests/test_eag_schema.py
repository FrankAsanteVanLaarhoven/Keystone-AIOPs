"""EAG-Bench (Phase B) — the action-case schema and its dependency-free validator.

Loads the validator by path so the test is independent of PYTHONPATH, then checks the
seed corpus validates and that the schema's guards (structure + the two conditionals)
actually reject malformed cases."""

import importlib.util
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EAG = os.path.join(ROOT, "benchmarks", "eag_bench")
CASES = os.path.join(EAG, "cases")


def _load_validator():
    spec = importlib.util.spec_from_file_location("eag_validate", os.path.join(EAG, "validate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = _load_validator()
SCHEMA = V.load_schema()


def _base():
    with open(os.path.join(CASES, "cloud_iam.attach_admin_policy.deny.json")) as f:
        return json.load(f)


def _case(**over):
    c = _base()
    c.update(over)
    return c


def test_all_seed_cases_validate_clean():
    files = [f for f in os.listdir(CASES) if f.endswith(".json")]
    assert files, "no seed cases found"
    for name in files:
        with open(os.path.join(CASES, name)) as f:
            case = json.load(f)
        assert V.validate_case(case, SCHEMA) == [], f"{name}: {V.validate_case(case, SCHEMA)}"


def test_unexpected_field_rejected():
    errs = V.validate_case(_case(surprise=1), SCHEMA)
    assert any("unexpected field 'surprise'" in e for e in errs)


def test_missing_required_field_rejected():
    c = _base()
    del c["risk_level"]
    errs = V.validate_case(c, SCHEMA)
    assert any("missing required field 'risk_level'" in e for e in errs)


def test_bad_enum_rejected():
    errs = V.validate_case(_case(risk_level="apocalyptic"), SCHEMA)
    assert any("risk_level" in e and "not in" in e for e in errs)


def test_bad_case_id_pattern_rejected():
    errs = V.validate_case(_case(case_id="Not Valid ID"), SCHEMA)
    assert any("case_id" in e and "match" in e for e in errs)


def test_deny_verdict_must_have_never_sentinel():
    c = _base()  # a deny case
    c["side_effect_sentinel"] = {**c["side_effect_sentinel"], "expected_timing": "after_allow"}
    errs = V.validate_case(c, SCHEMA)
    assert any("expected_timing" in e and "never" in e for e in errs)


def test_gated_verdict_requires_an_approver():
    c = _case(expected_verdict="require_human")
    c["required_gate"] = True
    c["required_approvers"] = 0
    errs = V.validate_case(c, SCHEMA)
    assert any("required_approvers" in e for e in errs)
