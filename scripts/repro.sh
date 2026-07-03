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
echo ">> [1/3] test suite (make test)"
"$PY" -m pytest -q

echo ""
echo ">> [2/3] benchmark scoreboard - absolute targets gate the exit code;"
echo "         allow-p99 spread is informational here (a container/shared host"
echo "         measures the environment, not the system - run natively with a"
echo "         pinned CPU governor for the dedicated-hardware spread claim)"
"$PY" bench/run_bench.py --spread-report-only

echo ""
echo ">> [3/3] evidence pack (make evidence)"
"$PY" scripts/build_evidence.py

echo ""
echo "=============================================================="
echo " REPRODUCTION PASSED - tests green, all benchmark targets met,"
echo " evidence pack regenerated. Compare docs/BENCHMARK.md against the"
echo " committed capture for this commit."
echo "=============================================================="
