"""T7 non-repudiation: signed checkpoints + append-only anchoring detect tail
truncation and rollback that a self-contained chain walk cannot see."""

from verdictplane.provenance import Ledger, merkle_root


def _ledger_with(tmp_path, n, name="l.jsonl", **extra):
    lg = Ledger(str(tmp_path / name))
    for i in range(n):
        lg.append({"n": i, **extra})
    return lg


def test_checkpoint_and_valid_extension(tmp_path):
    lg = _ledger_with(tmp_path, 5)
    anchor = lg.checkpoint()
    lg.append({"n": 5})
    lg.append({"n": 6})
    ok, reason = lg.verify_extends(anchor)
    assert ok, reason


def test_chain_verify_is_blind_to_truncation_but_anchor_is_not(tmp_path):
    lg = _ledger_with(tmp_path, 8)
    anchor = lg.checkpoint()  # count == 8
    lines = open(lg.path).read().splitlines()
    with open(lg.path, "w") as f:
        f.write("\n".join(lines[:5]) + "\n")  # drop the tail: a valid 5-entry prefix
    fresh = Ledger(lg.path)
    assert fresh.verify() == (True, None)  # chain-only walk cannot see the truncation
    ok, reason = fresh.verify_extends(anchor)
    assert not ok and "truncat" in reason.lower()


def test_rollback_to_a_different_history_is_detected(tmp_path):
    lg = _ledger_with(tmp_path, 6)
    anchor = lg.checkpoint()
    forked = _ledger_with(tmp_path, 6, name="forked.jsonl", forked=True)  # same length, diff content
    ok, reason = forked.verify_extends(anchor)
    assert not ok and "rollback" in reason.lower()


def test_signed_anchor_verifies_and_detects_a_tampered_anchor(tmp_path):
    key = b"anchor-key-not-a-real-secret-0001"
    lg = _ledger_with(tmp_path, 4)
    anchor = lg.checkpoint(key=key)
    assert "hmac" in anchor
    ok, reason = lg.verify_extends(anchor, key=key)
    assert ok, reason
    forged = {**anchor, "count": 99}  # tamper the anchor -> signature no longer matches
    ok, reason = lg.verify_extends(forged, key=key)
    assert not ok and "signature" in reason.lower()


def test_empty_anchor_extends_genesis(tmp_path):
    lg = _ledger_with(tmp_path, 0)
    anchor = lg.checkpoint()
    assert anchor["count"] == 0
    lg.append({"n": 0})
    ok, reason = lg.verify_extends(anchor)
    assert ok and "genesis" in reason.lower()


def test_merkle_root_is_deterministic_and_order_committing():
    a = merkle_root(["aa", "bb", "cc"])
    assert a == merkle_root(["aa", "bb", "cc"])   # deterministic
    assert a != merkle_root(["bb", "aa", "cc"])   # order-sensitive
    assert merkle_root([]) != a                    # empty is distinct
