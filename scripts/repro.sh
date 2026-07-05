#!/usr/bin/env sh
# One-command reproduction of VerdictPlane's evidence: the documented protocol
# (test suite + benchmark scoreboard + evidence pack) in a clean environment.
#
# Exits nonzero on ANY failure — tests red, a missed benchmark target, or a
# broken evidence run. Runs identically inside Docker (deploy/repro.Dockerfile)
# or locally:  PY=.venv/bin/python sh scripts/repro.sh
set -eu

PY="${PY:-python}"
export PYTHONPATH=""
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export VERDICTPLANE_ADVISORY=off

echo "=============================================================="
echo " VerdictPlane - reproduction protocol"
echo "   commit : ${VERDICTPLANE_REPRO_COMMIT:-<local working tree>}"
echo "   python : $("$PY" -V 2>&1)"
echo "   host   : $(uname -s -r -m)"
echo "=============================================================="

echo ""
echo ">> [1/4] test suite (make test)"
"$PY" -m pytest -q

echo ""
echo ">> [2/4] benchmark scoreboard - absolute targets gate the exit code;"
echo "         allow-p99 spread is informational here (a container/shared host"
echo "         measures the environment, not the system - run natively with a"
echo "         pinned CPU governor for the dedicated-hardware spread claim)"
"$PY" bench/run_bench.py --spread-report-only

echo ""
echo ">> [3/4] EAG-Bench EIGS-100 scoreboard (benchmarks/eag_bench/eag.py)"
echo "         computed from real track runs; exits nonzero on EIGS < 95 or ANY"
echo "         critical failure. Reproduces the headline governance score + the"
echo "         self-owned real slice (unscored) in this clean environment."
"$PY" benchmarks/eag_bench/eag.py

echo ""
echo ">> [4/4] evidence pack (make evidence)"
"$PY" scripts/build_evidence.py

echo ""
echo "=============================================================="
echo " REPRODUCTION PASSED - tests green, all benchmark targets met,"
echo " EIGS scoreboard recomputed, evidence pack regenerated. This proves"
echo " the results are REPRODUCIBLE from a clean environment; it is not, by"
echo " itself, third-party VALIDATION (an independent reviewer critiquing the"
echo " corpus + labels). Compare docs/BENCHMARK.md and docs/EAG_BENCH.md"
echo " against the committed captures for this commit."
echo "=============================================================="
