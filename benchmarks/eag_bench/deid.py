"""EAG-Bench — de-identification safety rail for real-trace ingestion (hard pipeline gate).

Before any non-synthetic trace becomes a corpus case it must pass through here. Two parts:

  1. de-identify — reuse `verdictplane.interceptor.redact` (masks secret-named keys, truncates long
     values) on the carrier fields, then pattern-scrub PII values (emails, IPs, SSNs, card numbers,
     cloud keys, private keys, JWTs) in the known text/argument fields.
  2. GATE — re-scan the WHOLE de-identified record for any residual secret/PII. If anything remains
     (e.g. PII that slipped into an unexpected field), the record is REJECTED: non-zero exit, no file
     written. Privacy FAILS the pipeline; it does not warn. De-identified output is always tagged
     `source: anonymized` (never `real`).

CLI:  python benchmarks/eag_bench/deid.py <input.json ...> --out <dir>
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

from verdictplane.interceptor import redact

SECRET_KEY = re.compile(
    r"password|passwd|secret|token|api_?key|authorization|credential|private_key", re.IGNORECASE)

PII = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    "aws_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}"),
}

TEXT_FIELDS = ("title", "description", "reproduction_notes", "narrative")


def _clean_str(s: str) -> str:
    for name, rx in PII.items():
        s = rx.sub(f"[REDACTED:{name}]", s)
    return s


def _pattern_clean(node):
    if isinstance(node, dict):
        return {k: _pattern_clean(v) for k, v in node.items()}
    if isinstance(node, list):
        return [_pattern_clean(v) for v in node]
    if isinstance(node, str):
        return _clean_str(node)
    return node


def deidentify_case(case: dict) -> dict:
    """Return a de-identified deep copy: carrier fields scrubbed (redact + PII patterns)."""
    c = json.loads(json.dumps(case))
    if isinstance(c.get("action"), dict) and "arguments" in c["action"]:
        c["action"]["arguments"] = _pattern_clean(redact(c["action"]["arguments"]))
    for fld in TEXT_FIELDS:
        if isinstance(c.get(fld), str):
            c[fld] = _clean_str(c[fld])
    for step in c.get("steps", []) if isinstance(c.get("steps"), list) else []:
        if isinstance(step.get("arguments"), dict):
            step["arguments"] = _pattern_clean(redact(step["arguments"]))
        if isinstance(step.get("note"), str):
            step["note"] = _clean_str(step["note"])
    return c


def scan(node, path: str, findings: list) -> None:
    """Recursively flag any residual secret/PII ANYWHERE in the record (the gate scanner)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if SECRET_KEY.search(str(k)) and not (isinstance(v, str) and v == "[REDACTED]"):
                findings.append((f"{path}.{k}", "secret_key", str(v)[:40]))
            scan(v, f"{path}.{k}" if path else str(k), findings)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            scan(v, f"{path}[{i}]", findings)
    elif isinstance(node, str):
        for name, rx in PII.items():
            for m in rx.finditer(node):
                findings.append((path, name, m.group(0)))


def scan_case(case: dict) -> list:
    findings: list = []
    scan(case, "", findings)
    return findings


def ingest(case: dict) -> tuple[bool, dict, list]:
    """Hard gate: de-identify, then re-scan the whole record. ok=False if anything still leaks."""
    clean = deidentify_case(case)
    clean["source"] = "anonymized"  # de-identified real data is anonymized, never 'real'
    residual = scan_case(clean)
    return (len(residual) == 0, clean, residual)


def main(argv: list) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    rejected = 0
    for pattern in args.inputs:
        for path in sorted(glob.glob(pattern)):
            with open(path) as f:
                case = json.load(f)
            ok, clean, residual = ingest(case)
            name = os.path.basename(path)
            if not ok:
                rejected += 1
                print(f"REJECT {name}: residual after de-id -> {residual[:3]}")
                continue  # no file written
            with open(os.path.join(args.out, name), "w") as f:
                json.dump(clean, f, indent=2)
                f.write("\n")
            print(f"ok     {name} -> de-identified (source=anonymized)")
    if rejected:
        print(f"\n{rejected} record(s) REJECTED — privacy gate failed the pipeline")
        return 1
    print("\nall records de-identified and cleared the gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
