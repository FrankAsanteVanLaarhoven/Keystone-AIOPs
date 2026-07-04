"""Dependency-free validator for EAG-Bench action cases.

Interprets the subset of JSON Schema used by ``schema/action_case.schema.json`` (which
stays the single source of truth) so the corpus validates with the stdlib alone —
consistent with VerdictPlane's no-extra-dependencies posture. Supported keywords:
type, const, enum, pattern, minLength, minimum, minItems, uniqueItems, items,
required, properties, additionalProperties(false), allOf, if/then/else.

CLI:
    python benchmarks/eag_bench/validate.py [case.json ...]
    # no args -> validate every benchmarks/eag_bench/cases/*.json
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "schema", "action_case.schema.json")
CASES_DIR = os.path.join(HERE, "cases")

_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _type_ok(value, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def _validate(node, schema: dict, path: str, errors: list) -> None:
    where = path or "<root>"

    t = schema.get("type")
    if t is not None and not _type_ok(node, t):
        errors.append(f"{where}: expected type {t}, got {type(node).__name__}")
        return  # remaining checks assume the type held

    if "const" in schema and node != schema["const"]:
        errors.append(f"{where}: must equal {schema['const']!r}, got {node!r}")
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{where}: {node!r} not in {schema['enum']}")

    if isinstance(node, str):
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{where}: {node!r} does not match /{schema['pattern']}/")
        if "minLength" in schema and len(node) < schema["minLength"]:
            errors.append(f"{where}: shorter than minLength {schema['minLength']}")

    if isinstance(node, (int, float)) and not isinstance(node, bool):
        if "minimum" in schema and node < schema["minimum"]:
            errors.append(f"{where}: {node} < minimum {schema['minimum']}")

    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errors.append(f"{where}: fewer than minItems {schema['minItems']}")
        if schema.get("uniqueItems"):
            seen: list = []
            for item in node:
                if item in seen:
                    errors.append(f"{where}: duplicate item {item!r}")
                seen.append(item)
        item_schema = schema.get("items")
        if item_schema is not None:
            for i, item in enumerate(node):
                _validate(item, item_schema, f"{path}[{i}]", errors)

    if isinstance(node, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{where}: missing required field {req!r}")
        if schema.get("additionalProperties") is False:
            for key in node:
                if key not in props:
                    errors.append(f"{where}: unexpected field {key!r}")
        for key, subschema in props.items():
            if key in node:
                _validate(node[key], subschema, f"{path}.{key}" if path else key, errors)

    if "if" in schema:
        cond: list = []
        _validate(node, schema["if"], path, cond)
        branch = "then" if not cond else "else"
        if branch in schema:
            _validate(node, schema[branch], path, errors)
    for sub in schema.get("allOf", []):
        _validate(node, sub, path, errors)


def load_schema(path: str = SCHEMA_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def validate_case(case: dict, schema: dict | None = None) -> list:
    """Return a list of human-readable errors; an empty list means the case is valid."""
    schema = load_schema() if schema is None else schema
    errors: list = []
    _validate(case, schema, "", errors)
    return errors


def main(argv: list) -> int:
    schema = load_schema()
    files = argv or sorted(glob.glob(os.path.join(CASES_DIR, "*.json")))
    if not files:
        print("no case files found")
        return 1
    bad = 0
    for f in files:
        with open(f) as fh:
            case = json.load(fh)
        errs = validate_case(case, schema)
        name = os.path.basename(f)
        if errs:
            bad += 1
            print(f"FAIL {name}")
            for e in errs:
                print(f"     - {e}")
        else:
            print(f"ok   {name}  ({case.get('case_id')})")
    print(f"\n{len(files) - bad}/{len(files)} cases valid")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
