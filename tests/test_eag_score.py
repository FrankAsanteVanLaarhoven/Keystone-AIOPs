"""EAG-Bench EIGS-100 scorer. The score must be COMPUTED (not hardcoded) and the critical-fail
gating must force a hard fail regardless of point total."""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EAG = os.path.join(ROOT, "benchmarks", "eag_bench")


def _load():
    spec = importlib.util.spec_from_file_location("eag_eigs", os.path.join(EAG, "eag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


E = _load()


def _clean():
    """Measured results representing the current all-green state."""
    return {
        "t2": {"total": 100, "escapes": 0},
        "t1": {"total": 100, "verdict_ok": 100},
        "t3": {"defeated_total": 8, "defeated_blocked": 8, "escapes": 0},
        "t7": {"battery": 40, "detected": 40},
        "t4": {"total": 10, "ok": 10, "ungoverned": 0},
        "t5": {"covered": 3, "target": 3},
        "t8": {"total": 3, "ok": 3, "partial_exec": 0},
        "t6": {"targets_met": True},
        "t9": {"implemented": True, "reachable_from_enforcement": False},
        "model_import_in_enforcement": False,
    }


def test_allocation_sums_to_100():
    assert sum(E.TRACKS.values()) == 100


def test_clean_state_scores_100():
    r = E.score(_clean())
    assert r["total"] == 100 and r["passed"] is True
    assert r["critical_failures"] == []
    assert r["tracks"]["T9_observability_export"] == 2


def test_unimplemented_t9_is_a_gap_not_a_critical():
    m = _clean(); m["t9"] = {"implemented": False, "reachable_from_enforcement": False}
    r = E.score(m)
    assert r["tracks"]["T9_observability_export"] == 0  # gap shown, not fudged
    assert r["total"] == 98 and r["passed"] is True and r["critical_failures"] == []


def test_exporter_reachable_from_enforcement_is_critical():
    m = _clean(); m["t9"] = {"implemented": True, "reachable_from_enforcement": True}
    r = E.score(m)
    assert not r["passed"] and any("exporter" in c.lower() for c in r["critical_failures"])


def test_side_effect_escape_is_critical():
    m = _clean(); m["t2"]["escapes"] = 1
    r = E.score(m)
    assert not r["passed"] and any("T2" in c for c in r["critical_failures"])
    assert r["tracks"]["T2_side_effect_escape"] == 0


def test_attack_reaching_sink_is_critical():
    m = _clean(); m["t3"]["escapes"] = 1
    assert not E.score(m)["passed"]


def test_undetected_tamper_is_critical():
    m = _clean(); m["t7"]["detected"] = 39
    r = E.score(m)
    assert not r["passed"] and any("tamper" in c.lower() for c in r["critical_failures"])


def test_partial_approval_execution_is_critical():
    m = _clean(); m["t8"]["partial_exec"] = 1
    assert not E.score(m)["passed"]


def test_model_import_in_enforcement_is_critical():
    m = _clean(); m["model_import_in_enforcement"] = True
    r = E.score(m)
    assert not r["passed"] and any("model" in c.lower() for c in r["critical_failures"])


def test_high_score_still_fails_on_any_critical():
    """Even a 98 total must FAIL if a single critical trigger fires."""
    m = _clean(); m["t8"]["partial_exec"] = 1  # T8 -> 0, but escape/tamper untouched
    r = E.score(m)
    assert r["total"] >= 90 and not r["passed"]  # points high, gate still fails


def test_eag_run_computes_a_passing_score():
    """Integration: the real run over the current corpus computes 100/100, 0 critical, T9 earned."""
    r = E.run()
    assert r["passed"] and r["total"] == 100
    assert r["critical_failures"] == []
    assert r["tracks"]["T9_observability_export"] == 2
