"""EAG-Bench Side-Effect Escape harness — the headline 0-escape result, wired into
`make test`. Includes a negative test proving the metric is not vacuous: under a
permissive policy the harness must REPORT escapes."""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EAG = os.path.join(ROOT, "benchmarks", "eag_bench")


def _load():
    spec = importlib.util.spec_from_file_location("eag_harness", os.path.join(EAG, "harness.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


H = _load()


def test_zero_escapes_across_corpus(tmp_path):
    rep = H.run(workdir=str(tmp_path))
    n = rep["total_cases"]
    assert n == 100
    assert rep["escapes"] == 0, [r["case_id"] for r in rep["results"] if r["escaped"]]
    assert rep["verdict_correct"] == n
    assert rep["ledger_complete"] == n
    assert rep["positive_path_ok"] == n
    assert rep["chain_intact"] == n
    assert rep["passed"]


def test_metric_is_not_vacuous(tmp_path):
    # A permissive allow-everything policy: deny / never cases now execute their side
    # effect, so the harness MUST report escapes and MUST NOT pass. Proves the 0 above
    # is a measured result, not a harness that always says zero.
    permissive = tmp_path / "permissive.yaml"
    permissive.write_text("default: allow\nrules: []\n")
    rep = H.run(policy_path=str(permissive), workdir=str(tmp_path / "w"))
    assert rep["escapes"] > 0
    assert not rep["passed"]
